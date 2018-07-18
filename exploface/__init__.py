import os
import elanwriter
import numpy as np
import pathlib
import pandas as pd
import warnings

from exploface.conversions import get_time_stamp_format_openface
import exploface.conversions
import exploface.extraction
import exploface.analysis

def get_info(csv_path, max_len_col_names=10):
    """
    Returns some basic information on the openface file.
    Return: dict with information
    csv_path: path to the openface csv output file
    """
    info = {}
    df = pd.read_csv(csv_path,skipinitialspace=True)
    cols = list(set(df.columns))
    nr_of_cols = len(cols)
    if nr_of_cols >= max_len_col_names:
        cols = cols[0:max_len_col_names]+["..."]

    info.update({"column_names": cols})
    info.update({"number_of_columns": nr_of_cols})
    info.update({"duration": \
        df["timestamp"][len(df["timestamp"])-1]-df["timestamp"][0]})
    info.update({"time_resolution": \
        df["timestamp"][1] - df["timestamp"][0]})

    return info

def get_statistics( csv_path,
                    round_to = 2,
                    column_selection = None,
                    skip_seconds_at_end=0,
                    intensity_threshold=0.8,
                    time_threshold=0.1,
                    smooth_time_threshold = 0.1,
                    uncertainty_threshold=0.9,
                    ):
    """
    Return some statistics of the openface file.
    Return: dict with statistics
    csv_path: path to the openface csv output file
    round_to: rounds the numbers to those amount of decimals.
    Other parameters see write_elan_file()
    """
    df = pd.read_csv(csv_path,skipinitialspace=True)
    df_timestamps = get_time_stamp_format_openface(df,
                                    skip_seconds_at_end= skip_seconds_at_end,
                                    intensity_threshold= intensity_threshold,
                                    time_threshold= time_threshold,
                                    smooth_time_threshold = smooth_time_threshold,
                                    uncertainty_threshold= uncertainty_threshold,
                                    )

    if not column_selection:
        column_selection = set(df_timestamps["au"])

    list_nr_detections = []
    ave_length = []
    std_ave_length = []
    au_dataframe = []
    for au in column_selection:
        if au in list(df_timestamps["au"]):
            stamps = df_timestamps[df_timestamps["au"]==au]
            nr_detections = len(stamps)
            duration = stamps["end"]-stamps["start"]

            average_length_detection = duration.mean()
            std_average_length_detection = duration.std()

            au_dataframe.append(au)
            list_nr_detections.append(nr_detections)
            ave_length.append(average_length_detection)
            std_ave_length.append(std_average_length_detection)

    if len(list_nr_detections)>0:
        df_res = pd.DataFrame({\
                    "nr_detections":pd.Series(list_nr_detections, index=au_dataframe),\
                    "average_length_detection":pd.Series(average_length_detection, index=au_dataframe),\
                    "std_average_length_detection":pd.Series(std_average_length_detection, index=au_dataframe),\
                    })
    else:
        df_res = pd.DataFrame()

    return df_res.sort_index()


def get_time_stamp(csv_path, 
                    skip_seconds_at_end=0,
                    intensity_threshold=0.8,
                    time_threshold=0.1,
                    smooth_time_threshold = 0.1,
                    uncertainty_threshold=0.9
                    ):
    """
    Generates a timestamp formatted pandas.DataFrame. This contains on a row
    a detection of an action unit and its start and end times.
    Return: pandas dataframe with timestamps
    csv_path: path to the openface csv output file
    Other parameters see write_elan_file()
    ...
    """
    df = pd.read_csv(csv_path,skipinitialspace=True )

    df_timestamps = get_time_stamp_format_openface(df,
                                    skip_seconds_at_end= skip_seconds_at_end,
                                    intensity_threshold= intensity_threshold,
                                    time_threshold= time_threshold,
                                    smooth_time_threshold = smooth_time_threshold,
                                    uncertainty_threshold= uncertainty_threshold,
                                    )
    return df_timestamps

def write_elan_file(csv_path, 
                    output_path=None,
                    video_path=None,
                    column_selection = None,
                    skip_seconds_at_end=0,
                    intensity_threshold=0.8,
                    time_threshold=0.1,
                    smooth_time_threshold = 0.1,
                    uncertainty_threshold=0.9,
                    ):
    """
    Generates an Elan file for csv_path (an openface output file)
    Return: pandas dataframe with timestamp formatted openface output
    csv_path: path to the openface csv output file
    output_path: 
    video_path: 
    column_selection: 
    skip_seconds_at_end: 
    intensity_threshold: 
    time_threshold: 
    smooth_time_threshold: 
    uncertainty_threshold: 
    """
    df_timestamps = get_time_stamp(csv_path, 
                    skip_seconds_at_end=skip_seconds_at_end,
                    intensity_threshold=intensity_threshold,
                    time_threshold=time_threshold,
                    smooth_time_threshold = smooth_time_threshold,
                    uncertainty_threshold=uncertainty_threshold
                    )

    if not column_selection:
        column_selection = set(df_timestamps["au"])

    ##
    # Make the Elan file
    ##
    if output_path:
        output_directory = os.path.dirname(output_path)
        output_filename = os.path.basename(output_path)
        video_dir = os.path.dirname(video_path)
        video_filename = os.path.basename(video_path)

        if video_dir == "":
            video_dir = "."

        if os.path.isfile(video_path):
            rel_video_path = os.path.join( os.path.relpath(video_dir, output_directory), video_filename )
        else:
            #warnings.warn("No video file found for the elan file. Video file: {}".format(video_path))
            rel_video_path = "video_not_found"

        ed = elanwriter.ElanDoc(rel_video_path)
        
        ##
        # Start looping over the AUs
        for au in column_selection:
            
            times = df_timestamps[df_timestamps["au"] == au]
            #print(au, len(times))
            for i in range(len(times)):
                annotation_name = times.iloc[i]["au"]
                if "modifier" in times.columns:
                    if times.iloc[i]["modifier"] and not np.isnan(times.iloc[i]["modifier"]):
                        annotation_name = "I="+str(times.iloc[i]["modifier"])

                ed.add_annotation((1000*times.iloc[i]["start"], 1000*times.iloc[i]["end"]), 
                                  annotation_name, tier_name=times.iloc[i]["au"])
            if len(times) == 0:
                ed.add_annotation((0,0.1), 
                                  "", au)

        ed.write(output_path)

    return df_timestamps
