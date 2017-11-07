
import numpy as np

def getSuccessTimes(df):
    return getActivationTimes(df, emo_key="success", method="threshold")
def getFailTimes(df):
    return getActivationTimes(df, emo_key="success", threshold= 0, method="threshold", inverse_threshold=True)

def getConfidenceTimes(df, confidence_threshold = 0.99):
    return getActivationTimes(df, emo_key="confidence", threshold=confidence_threshold)
def getUnConfidenceTimes(df, confidence_threshold = 0.99):
    return getActivationTimes(df, emo_key="confidence", threshold=confidence_threshold, inverse_threshold=True)

def getActivationTimes(df, emo_key, threshold=1, method="threshold", inverse_threshold = False, time_threshold=None, time_gap_smoothing=None, confidence_cut = None):
    if method == "mean":
        threshold_x_mean = threshold * df[emo_key].mean()
        #detected = np.all(
        detected = df[emo_key] >= threshold_x_mean
    elif method == "threshold":
        if inverse_threshold:
            detected = df[emo_key] <= threshold
        else: 
            detected = df[emo_key] >= threshold

    start = False
    times = []
    time_entry = []
    for i in range(len(df)):
        if detected[i]:
            if not start:
                start = True
                time_entry.append(df.iloc[i]["timestamp"])
            if i == len(df)-1:
                print("The end!")
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

    if confidence_cut:
        

    return times