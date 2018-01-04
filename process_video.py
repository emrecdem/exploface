
import numpy as np


def generateEmotionsFromAU(df):

    df["happy"] = (df["AU06_r"]+df["AU12_r"])/2
    df["surprise"]=(df["AU01_r"]+df["AU02_r"]+df["AU05_r"]+df["AU26_r"])/4
    df["sad"]=(df["AU01_r"]+df["AU04_r"]+df["AU15_r"])/3
    df["fear"]=(df["AU01_r"]+df["AU02_r"]+df["AU04_r"]+df["AU05_r"]+df["AU07_r"]+df["AU20_r"]+df["AU26_r"])/7 
    df["anger"]=(df["AU04_r"]+df["AU05_r"]+df["AU07_r"]+df["AU23_r"])/4
    df["disgust"]=(df["AU09_r"]+df["AU15_r"])/2

    df["happy_c"] = (df["AU06_c"]+df["AU12_c"])/2
    df["surprise_c"]=(df["AU01_c"]+df["AU02_c"]+df["AU05_c"]+df["AU26_c"])/4
    df["sad_c"]=(df["AU01_c"]+df["AU04_c"]+df["AU15_c"])/3
    df["fear_c"]=(df["AU01_c"]+df["AU02_c"]+df["AU04_c"]+df["AU05_c"]+df["AU07_c"]+df["AU20_c"]+df["AU26_c"])/7 
    df["anger_c"]=(df["AU04_c"]+df["AU05_c"]+df["AU07_c"]+df["AU23_c"])/4
    df["disgust_c"]=(df["AU09_c"]+df["AU15_c"])/2

    return df



def getSuccessTimes(df):
    return getActivationTimes(df, emo_key="success", method="threshold")
def getFailTimes(df):
    return getActivationTimes(df, emo_key="success", threshold= 0, method="threshold", inverse_threshold=True)

def getConfidenceTimes(df, confidence_threshold = 0.99):
    return getActivationTimes(df, emo_key="confidence", threshold=confidence_threshold)
def getUnConfidenceTimes(df, confidence_threshold = 0.99):
    return getActivationTimes(df, emo_key="confidence", threshold=confidence_threshold, inverse_threshold=True)

def getActivationTimes(df, emo_key, threshold=1, method="threshold",
                        inverse_threshold = False, time_threshold=None, 
                        time_gap_smoothing=None, confidence_cut = None):


    if method == "mean":
        threshold_x_mean = threshold * df[emo_key].mean()
        #detected = np.all(
        detected = df[emo_key] >= threshold_x_mean
    elif method == "threshold":
        if inverse_threshold:
            detected = df[emo_key] <= threshold
        else: 
            detected = df[emo_key] >= threshold

    if confidence_cut:
        confident = df["confidence"] >= 0.8
        detected = detected & confident

    start = False
    times = []
    time_entry = []
    for i in range(len(df)):
        if detected[i]:
            if not start:
                start = True
                time_entry.append(df.iloc[i]["timestamp"])
            if i == len(df)-1:
                time_entry.append(df.iloc[i]["timestamp"])
                times.append(time_entry)                
        elif start:
            start = False
            time_entry.append(df.iloc[i]["timestamp"])
            times.append(time_entry)
            time_entry = []

    # This filters through the time slots and merges two time slots that 
    # are less than time_gap_smoothing seconds apart
    if time_gap_smoothing:
        new_times = []
        for i in range(len(times)-1):
            t = times[i]
            tp = times[i+1]
            if (tp[0]-t[1]) < time_gap_smoothing:
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
            if (t[1]-t[0]) > time_threshold:
                new_times.append(t)
        times = new_times

    #if confidence_cut:
        

    return times



def analyse_video(verbose, inputpath, filename, path, filename_no_ext, outputpath, openface_feat_exe):
    # CHECK THE ARGUMENTS
    if not os.path.isfile(inputpath):
        raise Exception("Input file and path do not exist:", inputpath)
    if not os.path.isdir(outputpath):
        raise Exception("Output path does not exist:", outputpath)
    if not os.path.isfile(openface_feat_exe):
        raise Exception("This openface feature extraction executable does not exist: ", openface_feat_exe)

    if verbose:
        print("Input file: {}".format(inputpath))
        print("Output dir: {}".format(outputpath))
        print("Openface feature extraction executable: ", openface_feat_exe)

    # RUN OPENFACE
    if verbose: print("Starting openface feature extraction")
    output_file_csv = os.path.join(path, filename_no_ext+".csv")
    os.system(openface_feat_exe+" -f "+inputpath+" -of "+output_file_csv+"> output.temp")
    if verbose: print("Finished openface feature extraction, reading in csv file")
    datafile = pd.read_csv(output_file_csv,skipinitialspace=True )

    # GENERATE emotions from the ActionUnits (AU)
    datafile = process_AU.generateEmotionsFromAU(datafile)

    # GENERATE time intervals for successful detection of the face and confidences
    times_succes = process_AU.getSuccessTimes(datafile)
    times_confident = process_AU.getUnConfidenceTimes(datafile, confidence_threshold = 0.8)
    times_fail = process_AU.getFailTimes(datafile)

    # PLOT SOME STATS
    fig = plt.figure(figsize=(10,10))
    plt.subplot(2,2,1)
    plt.plot(datafile['timestamp'], datafile["confidence"], label="confidence")
    y=0.99
    for t in times_confident:
        plt.plot((t[0],t[1]), (y,y), color="red")
    plt.xlabel("Time (sec)")
    plt.ylabel("Confidence")
    plt.legend()

    plt.subplot(2,2,2)
    plt.plot(datafile['timestamp'], datafile['pose_Tx'])
    plt.xlabel("Time (sec)")
    plt.ylabel("Side rotation head (degrees)")

    fig.subplots_adjust(wspace=0.3)#, hspace=0)

    plt.savefig(os.path.join(path, filename_no_ext+".pdf"))

    plt.close()



    # WRITE an Elan file with the success and confidence intervals
    ed = elanwriter.ElanDoc(inputpath)
    for i in range(len(times_confident)):
        ed.add_annotation((1000*times_confident[i][0], 1000*times_confident[i][1]), "<0.8", "Confidence")
    for i in range(len(times_fail)):
        ed.add_annotation((1000*times_fail[i][0], 1000*times_fail[i][1]), "failure", "Detection failure")
    ed.write(os.path.join(path, filename_no_ext+".eaf"))

