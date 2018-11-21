import os
import elanwriter
import numpy as np
import pathlib
import pandas as pd
import warnings

import exploface.conversions
import exploface.extraction
import exploface.analysis
import exploface.visualization

__version__ = "0.0.0.dev6"

_FEAT_NAME_ID = "feature"

def get_info(csv_path, max_len_col_names=10):
    """
    Returns some basic information on the openface file.
    Return: dict with information
    csv_path: path to the openface csv output file
    """
    info = {}
    df = pd.read_csv(csv_path,skipinitialspace=True)
    cols = list(set(df.columns)) # Make a unique list of column names
    nr_of_cols = len(cols)
    if nr_of_cols >= max_len_col_names: # then dont output all names
        cols = cols[0:max_len_col_names]+["..."] 

    info.update({"column_names": cols})
    info.update({"number_of_columns": nr_of_cols})
    info.update({"duration": \
        df["timestamp"][len(df["timestamp"])-1]-df["timestamp"][0]})
    # Assuming constant resolution
    info.update({"time_resolution": \
        df["timestamp"][1] - df["timestamp"][0]})

    return info

def get_statistics( csv_path,
                    column_selection = None,
                    skip_seconds_at_end=0,
                    intensity_threshold=0.8,
                    time_threshold=0.1,
                    smooth_time_threshold = 0.1,
                    uncertainty_threshold=0.9,
                    ):
    """
    Returns some statistics of the openface file.
    Return: DataFrame with statistics
    csv_path: path to the openface csv output file
    Other parameters see write_elan_file()
    """

    ts = get_feature_time_series(csv_path)

    df_detections = get_detections(ts,
                                    skip_seconds_at_end= skip_seconds_at_end,
                                    intensity_threshold= intensity_threshold,
                                    time_threshold= time_threshold,
                                    smooth_time_threshold = smooth_time_threshold,
                                    uncertainty_threshold= uncertainty_threshold,
                                    )

    if not column_selection:
        column_selection = set(df_detections[_FEAT_NAME_ID])

    list_nr_detections = []
    ave_length = []
    std_ave_length = []
    au_dataframe = []
    for au in column_selection:
        if au in list(df_detections[_FEAT_NAME_ID]):
            detections = df_detections[df_detections[_FEAT_NAME_ID]==au]
            nr_detections = len(detections)
            duration = detections["end"]-detections["start"]

            average_length_detection = duration.mean()
            std_average_length_detection = duration.std()

            au_dataframe.append(au)
            list_nr_detections.append(nr_detections)
            ave_length.append(average_length_detection)
            std_ave_length.append(std_average_length_detection)

    if len(list_nr_detections)>0:
        df_res = pd.DataFrame({\
                    "nr_detections":pd.Series(list_nr_detections, index=au_dataframe),\
                    "average_length_detection":pd.Series(ave_length, index=au_dataframe),\
                    "std_average_length_detection":pd.Series(std_ave_length, index=au_dataframe),\
                    })
    else:
        df_res = pd.DataFrame()

    return df_res.sort_index()


def get_feature_time_series(csv_path):

    df = pd.read_csv(csv_path,skipinitialspace=True )

    return df

def get_detections(feature_time_series, 
                    skip_seconds_at_end=0,
                    intensity_threshold=0.8,
                    time_threshold=0.1,
                    smooth_time_threshold = 0.1,
                    uncertainty_threshold=0.9
                    ):
    """
    Generates a pandas.DataFrame with detections. This contains on every row
    a detection of an action unit and its start and end times.
    Return: pandas dataframe with timestamps
    csv_path: path to the openface csv output file
    Other parameters see write_elan_file()
    ...
    """
    df = feature_time_series#pd.read_csv(csv_path,skipinitialspace=True )

    AUs = []
    start_list = []
    end_list = []
    for c in df.columns:
        if "AU" in c and "_c" in c:

            times = extraction.get_activation_times(df, 
                emo_key = c,
                intensity_threshold = intensity_threshold,\
                confidence_cut = uncertainty_threshold,
                smooth_time_threshold = smooth_time_threshold,
                time_threshold = time_threshold,
                )

            for t in times:
                if t[0] < df["timestamp"].iloc[-1] - skip_seconds_at_end:
                    AUs.append(c.split("_")[0])
                    start_list.append(t[0])
                    end_list.append(t[1])

    return pd.DataFrame({"start": start_list, "end":end_list, _FEAT_NAME_ID: AUs})


def write_elan_file(detections, 
                    output_path=None,
                    video_path=None,
                    #column_selection = None,
                    ):
    """
    Generates an Elan file for the detections

    """
    elanwriter.write_elan_file(detections, video_path, output_path, 
        feature_col_name = _FEAT_NAME_ID)
