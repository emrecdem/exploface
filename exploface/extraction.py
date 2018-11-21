import pandas as pd


def get_activation_times(
                    df, 
                    emo_key, 
                    intensity_threshold=1, 
                    method="threshold",
                    confidence_cut = 0.9,
                    inverse_threshold = False, 
                    smooth_time_threshold = None,
                    time_threshold = 0.9,
#                    smooth_over_time_interval = None
                    ):
    # smooth_over_time_interval
    # If active: only after smooth_over_time_interval seconds of not active will detection of the parameter end
    # If not active: timestamps where the parameter is active for longer than a smooth_over_time_interval seconds will be recorded

    round_seconds_to_decimals = 2

    # Improve this implementation!
    #time_gap_smoothing = smooth_time_threshold

    if method == "mean":
        threshold_x_mean = intensity_threshold * df[emo_key].mean()
        detected = df[emo_key] >= threshold_x_mean
    elif method == "threshold":
        if inverse_threshold:
            detected = df[emo_key] <= intensity_threshold
        else: 
            detected = df[emo_key] >= intensity_threshold

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
    if smooth_time_threshold:
        new_times = []
        for i in range(len(times)-1):
            t = times[i]
            tp = times[i+1]
            if round((tp[0]-t[1]),round_seconds_to_decimals) <= smooth_time_threshold:
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
