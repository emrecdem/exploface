import pandas as pd


def generate_emotions_from_AU(df):
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



def get_success_times(df):
    return get_activation_times(df, emo_key="success", method="threshold")

def get_fail_times(df):
    return get_activation_times(df, emo_key="success", threshold= 0, method="threshold", inverse_threshold=True)

def get_confidence_times(df, confidence_threshold = 0.99):
    return get_activation_times(df, emo_key="confidence", threshold=confidence_threshold)

def get_unconfidence_times(df, confidence_threshold = 0.99):
    return get_activation_times(df, emo_key="confidence", threshold=confidence_threshold, inverse_threshold=True)

def get_activation_times(
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

    return times



"""
Now the dataframe needs to contain 
- feature_detected: if this is given, it will be used to select the times at the start of this function.
- feature_detected == None: then feature_intensity is used with intensity_threshold to get the times. In
                            this case if intensity_threshold is not given it is assumed to be 1.0
"""
def get_activation_dataframe(data, 
                            feature_intensity, smooth_over_time_interval, 
                            feature_detected=None, intensity_threshold=None):

    if feature_detected:
        times = get_activation_times(
            data, feature_detected, 
            threshold=1, method="threshold",
            smooth_over_time_interval=smooth_over_time_interval,
            inverse_threshold = False,
            )
    else:
        if not intensity_threshold:
            intensity_threshold = 1.0

        times = get_activation_times(
            data, feature_intensity, 
            threshold=intensity_threshold, method="threshold",
            smooth_over_time_interval=smooth_over_time_interval,
            inverse_threshold = False,
            )

    if len(times) > 0:
        start, end = list(zip(*times))
    else:
        start, end = [], []

    df_result = pd.DataFrame({"start": start, "end": end})

    mean = []
    std = []
    mean_confidence = []
    start = []
    end = []
    for i in range(len(df_result)):
        indices = (data["timestamp"]>df_result["start"][i]) & (data["timestamp"]<df_result["end"][i])

        i_mean = data[indices][feature_intensity].mean()
        i_std = data[indices][feature_intensity].std()
        i_mean_conf = data[indices]["confidence"].mean()
        
        # If feature_detected is given together with intensity_threshold, then 
        # you pick out the times that have an mean intensity>intensity_threshold
        if intensity_threshold and feature_detected:
            if i_mean >= intensity_threshold:
                start.append(df_result["start"][i])
                end.append(df_result["end"][i])
                mean.append(i_mean)
                std.append(i_std)
                mean_confidence.append(i_mean_conf)
        # If no intensity_threshold and feature_detected is given. The times will 
        # come from feature_intensity and that is what you want.
        else:
            start.append(df_result["start"][i])
            end.append(df_result["end"][i])
            mean.append(i_mean)
            std.append(i_std)
            mean_confidence.append(i_mean_conf)

    df_result = pd.DataFrame()#{"start": start, "end": end})
    df_result["start"] = start
    df_result["end"] = end
    df_result["mean_intensity"] = mean
    df_result["std_intensity"] = std
    df_result["mean_confidence"] = mean_confidence
    df_result["duration"] = df_result["end"] - df_result["start"]
        
    return df_result
