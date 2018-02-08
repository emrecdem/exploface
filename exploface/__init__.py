import os
import elanwriter
import numpy as np
import pathlib
import pandas as pd
import warnings

def generateEmotionsFromAU(df):
    # AU vary on a scale of 0-5
    df["happy_r"] = (df["AU06_r"]+df["AU12_r"])/(2)
    df["surprise_r"]=(df["AU01_r"]+df["AU02_r"]+df["AU05_r"]+df["AU26_r"])/(4)
    df["sad_r"]=(df["AU01_r"]+df["AU04_r"]+df["AU15_r"])/(3)
    df["fear_r"]=(df["AU01_r"]+df["AU02_r"]+df["AU04_r"]+df["AU05_r"]+df["AU07_r"]+df["AU20_r"]+df["AU26_r"])/(7)
    df["anger_r"]=(df["AU04_r"]+df["AU05_r"]+df["AU07_r"]+df["AU23_r"])/(4)
    df["disgust_r"]=(df["AU09_r"]+df["AU15_r"])/(2)

    df["happy_c"] = (df["AU06_c"]>0) & (df["AU12_c"]>0) #(df["AU06_c"]+df["AU12_c"])/2# (df["AU06_c"]>0 and df["AU12_c"]>0)  # 
    df["surprise_c"]=(df["AU01_c"]>0) & (df["AU02_c"]>0) & (df["AU05_c"]>0) & (df["AU26_c"]>0) #(df["AU01_c"]+df["AU02_c"]+df["AU05_c"]+df["AU26_c"])/4
    df["sad_c"]=(df["AU01_c"]>0) & (df["AU04_c"]>0) & (df["AU15_c"]>0)
    df["fear_c"]=(df["AU01_c"]>0) & (df["AU02_c"]>0) & (df["AU04_c"]>0) & (df["AU05_c"]>0) & (df["AU07_c"]>0) & (df["AU20_c"]>0) & (df["AU26_c"]>0)
    df["anger_c"]=(df["AU04_c"]>0) & (df["AU05_c"]>0) & (df["AU07_c"]>0) & (df["AU23_c"]>0)
    df["disgust_c"]=(df["AU09_c"]>0) & (df["AU15_c"]>0)

    return df



def getSuccessTimes(df):
    return getActivationTimes(df, emo_key="success", method="threshold")

def getFailTimes(df):
    return getActivationTimes(df, emo_key="success", threshold= 0, method="threshold", inverse_threshold=True)

def getConfidenceTimes(df, confidence_threshold = 0.99):
    return getActivationTimes(df, emo_key="confidence", threshold=confidence_threshold)

def getUnConfidenceTimes(df, confidence_threshold = 0.99):
    return getActivationTimes(df, emo_key="confidence", threshold=confidence_threshold, inverse_threshold=True)

def getActivationTimes(
                    df, 
                    emo_key, 
                    threshold=1, 
                    method="threshold",
                    confidence_cut = 0.9,
                    inverse_threshold = False, 
                    smooth_over_time_interval = None
                    ):
    # smooth_over_time_interval
    # If active: only after smooth_over_time_interval seconds of not active will detection of the parameter end
    # If not active: timestamps where the parameter is active for longer than a smooth_over_time_interval seconds will be recorded

    round_seconds_to_decimals = 2

    # Improve this implementation!
    time_threshold = smooth_over_time_interval
    time_gap_smoothing = smooth_over_time_interval

    if method == "mean":
        threshold_x_mean = threshold * df[emo_key].mean()
        detected = df[emo_key] >= threshold_x_mean
    elif method == "threshold":
        if inverse_threshold:
            detected = df[emo_key] <= threshold
        else: 
            detected = df[emo_key] >= threshold

    if confidence_cut:
        confident = df["confidence"] >= confidence_cut
        detected = detected & confident

    ##
    # Here we extract the activation times of the feature
    ##
    start = False
    times = []
    time_entry = []
    for i in range(len(df)):
        if detected[i]:
            if not start:
                start = True
                time_entry.append(round(df.iloc[i]["timestamp"], round_seconds_to_decimals))
            if i == len(df)-1:
                time_entry.append(round(df.iloc[i]["timestamp"], round_seconds_to_decimals))
                times.append(time_entry)                
        elif start:
            start = False
            time_entry.append(round(df.iloc[i-1]["timestamp"], round_seconds_to_decimals))
            times.append(time_entry)
            time_entry = []

    # This filters through the time slots and merges two time slots that 
    # are less than time_gap_smoothing seconds apart
    if time_gap_smoothing:
        new_times = []
        for i in range(len(times)-1):
            t = times[i]
            tp = times[i+1]
            if round((tp[0]-t[1]),round_seconds_to_decimals) <= time_gap_smoothing:
                times[i+1] = [t[0], tp[1]]
                times[i] = []
        new_times = []
        for i in range(len(times)):
            if len(times[i]) != 0:
                new_times.append(times[i])
        times = new_times      

    # This filters through the time slots and throughs out the ones 
    # that are shorter than time_threshold
    if time_threshold:
        new_times = []
        for t in times:
            if round((t[1]-t[0]),round_seconds_to_decimals) >= time_threshold:
                new_times.append(t)
        times = new_times

    ##
    # Here we make a data frame and add the timeslots and other information
    ##
    #print(times)
    #start, end = zip(*times)
    #df_result = pd.DataFrame({"start": start, "end": end})

    # Some stats on the activation times
    # nr_of_activations = len(times)
    # if nr_of_activations > 0:
    #     activation_length = np.array([t[1]-t[0] for t in times])
    #     total_activation_length = sum(activation_length)
    #     mean_activation_length = np.mean(activation_length)
    #     std_deviation_activation_length = np.std(activation_length)
    # else:
    #     total_activation_length = 0
    #     mean_activation_length = 0
    #     std_deviation_activation_length = 0

    # Some stats on the intensity of the feature
    return times



"""
Now the dataframe needs to contain 
"""
def get_activation_dataframe(data, feature_detected,feature_intensity, smooth_over_time_interval):#, threshold, threshold_method="threshold"):

    times = getActivationTimes(
        data, feature_detected, 
        threshold=1, method="threshold",
        smooth_over_time_interval=smooth_over_time_interval,
        inverse_threshold = False,
        )

    if len(times) > 0:
        start, end = list(zip(*times))
    else:
        start, end = [], []

    df_result = pd.DataFrame({"start": start, "end": end})
    df_result["duration"] = df_result["end"] - df_result["start"]

    mean = []
    std = []
    mean_confidence = []
    for i in range(len(df_result)):
        indices = (data["timestamp"]>df_result["start"][i]) & (data["timestamp"]<df_result["end"][i])

        i_mean = data[indices][feature_intensity].mean()
        i_std = data[indices][feature_intensity].std()
        mean.append(i_mean)
        std.append(i_std)
        
        i_mean_conf = data[indices]["confidence"].mean()
        mean_confidence.append(i_mean_conf)

    df_result["mean_intensity"] = mean
    df_result["std_intensity"] = std
    df_result["mean_confidence"] = mean_confidence
        
    return df_result


def write_elan_file(
    csv_filepath,
    threshold = 0.8,
    threshold_method = "threshold",
    smooth_over_time_interval=0.3,
    output_directory = None,
    video_directory = None,
    ):

    run_status = []

    filename_no_ext = os.path.basename(csv_filepath).split(".")[0]
    directory = os.path.dirname(csv_filepath)
    
    datafile = pd.read_csv(csv_filepath,skipinitialspace=True )
    datafile = generateEmotionsFromAU(datafile)
    
    # These will be the column names of the action units and the emotions
    columns = [c for c in datafile.columns if "_c" in c]#[c for c in datafile.columns if "AU" in c and "_c" in c]

    if video_directory:
        # If video_directory is given, the link in the elan file will point to a avi/mp4 video in the video_directory
        rel_video_path = os.path.join( os.path.relpath(video_directory, output_directory), filename_no_ext )
    elif output_directory:
        # If only a output_directory is given, it is assumed that the avi or mp4 video is in the input directory
        rel_video_path = os.path.join( os.path.relpath(directory, output_directory), filename_no_ext )
        video_directory = directory
    else:
        # If none of these directories is given, it is assumed that the elan file is saved in the directory
        # where an avi/mp4 video is present
        rel_video_path = filename_no_ext
        video_directory = directory

    if os.path.isfile(os.path.join(video_directory, filename_no_ext)+".avi"): rel_video_path+=".avi"
    elif os.path.isfile(os.path.join(video_directory, filename_no_ext)+".mp4"): rel_video_path+=".mp4"
    else: 
        warnings.warn("No video file found for the elan file({}), we searched in {} for avi and mp4 files".format(csv_filepath, video_directory))
        rel_video_path = "video_not_found"
        
    # Create an elan document
    ed = elanwriter.ElanDoc(rel_video_path)

    # First print a tier to indicate the confidence of openface
    times = getActivationTimes(datafile, "confidence", threshold=0.95, method=threshold_method, 
                                        smooth_over_time_interval=smooth_over_time_interval,
                                        inverse_threshold = True)
    for i in range(len(times)):
        ed.add_annotation((1000*times[i][0], 1000*times[i][1]), "<95%", tier_name="Confidence")
    if len(times)==0:
        ed.add_annotation((0,0), "", tier_name="Confidence")
        
    # Now walk over all the action units & emotions and add them to the elan file
    for c in columns:
        times = getActivationTimes(datafile, c, threshold=threshold, method=threshold_method, 
                                           smooth_over_time_interval=smooth_over_time_interval)
        
        c_intensity = c.replace("_c", "_r")
        if c_intensity in datafile.columns:
            df = get_activation_dataframe(datafile, 
                                                c, c_intensity, 
                                                smooth_over_time_interval=smooth_over_time_interval)
            
           
            for i in range(len(df)):
                start = df["start"][i]
                end = df["end"][i]
                #label =  str(round(df["duration"][i],2))+" sec, "
                label = "("+str(round(df["mean_intensity"][i],2))+"/5)"+" +/- "
                label += str(round(df["std_intensity"][i],2))

                #print(start, end, label)

                ed.add_annotation((1000*start, 1000*end), label, tier_name=c)
            if len(times)==0:
                ed.add_annotation((0,0), c, tier_name=c)
                
        else:
            run_status.append("No intensity for "+c)
    
    # Write out the elan file
    if output_directory:
        ed.write(os.path.join(output_directory, filename_no_ext+".eaf"))
    else:
        ed.write(os.path.join(directory, filename_no_ext+".eaf"))

    return run_status
