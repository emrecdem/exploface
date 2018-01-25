
import elanwriter
import numpy as np

def generateEmotionsFromAU(df):
    # AU vary on a scale of 0-5
    df["happy"] = (df["AU06_r"]+df["AU12_r"])/(2*5)
    df["surprise"]=(df["AU01_r"]+df["AU02_r"]+df["AU05_r"]+df["AU26_r"])/(4*5)
    df["sad"]=(df["AU01_r"]+df["AU04_r"]+df["AU15_r"])/(3*5)
    df["fear"]=(df["AU01_r"]+df["AU02_r"]+df["AU04_r"]+df["AU05_r"]+df["AU07_r"]+df["AU20_r"]+df["AU26_r"])/(7*5)
    df["anger"]=(df["AU04_r"]+df["AU05_r"]+df["AU07_r"]+df["AU23_r"])/(4*5)
    df["disgust"]=(df["AU09_r"]+df["AU15_r"])/(2*5)

    df["happy_c"] = (df["AU06_c"]+df["AU12_c"])/2# (df["AU06_c"]>0 and df["AU12_c"]>0)  # 
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

def getActivationTimes(
                    df, 
                    emo_key, 
                    threshold=1, 
                    method="threshold",
                    confidence_cut = 0.9,
                    inverse_threshold = False, 
                    smooth_over_time_interval = None
                    ):

    results = get_feature_summary(df, 
                                    emo_key, 
                                    threshold, 
                                    method,
                                    confidence_cut,
                                    inverse_threshold, 
                                    smooth_over_time_interval
                                    )

    return results["times"]

def get_feature_summary(
                        df, 
                        emo_key, 
                        threshold=1, 
                        method="threshold",
                        confidence_cut = 0.9,
                        inverse_threshold = False, 
                        smooth_over_time_interval = None
                        ):
    
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

    # Some stats on the activation times
    nr_of_activations = len(times)
    if nr_of_activations > 0:
        activation_length = np.array([t[1]-t[0] for t in times])
        total_activation_length = sum(activation_length)
        mean_activation_length = np.mean(activation_length)
        std_deviation_activation_length = np.std(activation_length)
    else:
        total_activation_length = 0
        mean_activation_length = 0
        std_deviation_activation_length = 0

    return {"times": times, 
            "total_activation_length":total_activation_length,
            "mean_activation_length":mean_activation_length, 
            "std_deviation_activation_length":std_deviation_activation_length}
