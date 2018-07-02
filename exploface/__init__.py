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


def get_info(csv_path):
    """
    Returns some basic information on the openface
    file.
    ...
    """
    info = {}
    df = pd.read_csv(csv_path,skipinitialspace=True)
    info.update({"columns": set(df.columns)})
    info.update({"length (sec)": \
        str(df["timestamp"][len(df["timestamp"])-1]-df["timestamp"][0])})
    info.update({"time resolution (sec)": \
        str(df["timestamp"][1] - df["timestamp"][0])})

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
    Return some statistics of the openface file.
    ...
    """
    df = pd.read_csv(csv_path,skipinitialspace=True)
    df_timestamps = get_time_stamp_format_openface(df,
                                    skip_seconds_at_end= skip_seconds_at_end,
                                    intensity_threshold= intensity_threshold,
                                    time_threshold= time_threshold,
                                    smooth_time_threshold = smooth_time_threshold,
                                    uncertainty_threshold= uncertainty_threshold,
                                    )

    aus = set(df_timestamps["au"])
    stats = {}
    for au in aus:
        stamps = df_timestamps[df_timestamps["au"]==au]
        nr_detections = len(stamps)
        stamps["duration"] = stamps["end"]-stamps["start"]
        average_length_detection = stamps["duration"].mean()
        std_average_length_detection = stamps["duration"].std()
        stats.update( \
            {au: {\
                "nr_detections": nr_detections, \
                "average_length_detection": average_length_detection, \
                "std_average_length_detection": std_average_length_detection\
                }
            })
        
    return stats


def write_elan_file(csv_path, 
                    output_path,
                    video_path,
                    column_selection = None,
                    skip_seconds_at_end=0,
                    intensity_threshold=0.8,
                    time_threshold=0.1,
                    smooth_time_threshold = 0.1,
                    uncertainty_threshold=0.9,
                    ):
    """
    action_unit_selection: list of AU strings. Or string containing "continuous" or "discrete"

    """

    ##
    # Fix the paths and read in the csv
    ##
    output_directory = os.path.dirname(output_path)
    output_filename = os.path.basename(output_path)
    video_dir = os.path.dirname(video_path)
    video_filename = os.path.basename(video_path)

    if os.path.isfile(video_path):
        rel_video_path = os.path.join( os.path.relpath(video_dir, output_directory), video_filename )
    else:
        warnings.warn("No video file found for the elan file. Video file: {}".format(video_path))
        rel_video_path = "video_not_found"

    ##
    # Get the timestamps
    ##
    df = pd.read_csv(csv_path,skipinitialspace=True )

    df_timestamps = get_time_stamp_format_openface(df,
                                    skip_seconds_at_end= skip_seconds_at_end,
                                    intensity_threshold= intensity_threshold,
                                    time_threshold= time_threshold,
                                    smooth_time_threshold = smooth_time_threshold,
                                    uncertainty_threshold= uncertainty_threshold,
                                    )
    
    if not column_selection:
        column_selection = set(df_timestamps["au"])

    ##
    # Make the Elan file
    ##
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

# def write_elan_file_from_stamps(
#     data_frame,
#     output_path,
#     video_path,
#     selected_tiers = None
#     ):

#     if selected_tiers:
#         unique_tiers = selected_tiers
#     else:
#         unique_tiers = set(data_frame["au"])
    
#     ##
#     # Initiate the video path for the Elan file
#     output_directory = os.path.dirname(output_path)
#     output_filename = os.path.basename(output_path)
#     video_dir = os.path.dirname(video_path)
#     video_filename = os.path.basename(video_path)

#     if os.path.isfile(video_path):
#         rel_video_path = os.path.join( os.path.relpath(video_dir, output_directory), video_filename )
#     else:
#         warnings.warn("No video file found for the elan file({}), we searched in {} for avi and mp4 files".format(csv_filepath, video_directory))
#         rel_video_path = "video_not_found"
    
#     ##
#     # Make the Elan object
#     ed = elanwriter.ElanDoc(rel_video_path)
    
#     ##
#     # Start looping over the AUs
#     for au in unique_tiers:
        
#         times = data_frame[data_frame["au"] == au]
#         #print(au, len(times))
#         for i in range(len(times)):
#             annotation_name = times.iloc[i]["au"]
#             if "modifier" in times.columns:
#                 if times.iloc[i]["modifier"] and not np.isnan(times.iloc[i]["modifier"]):
#                     annotation_name = "I="+str(times.iloc[i]["modifier"])

#             ed.add_annotation((1000*times.iloc[i]["start"], 1000*times.iloc[i]["end"]), 
#                               annotation_name, tier_name=times.iloc[i]["au"])
#         if len(times) == 0:
#             ed.add_annotation((0,0.1), 
#                               "", au)

#     ed.write(output_path)


# def write_elan_file_from_openface(
#     csv_filepath,
#     intensity_threshold = None,
#     threshold_method = "threshold",
#     smooth_over_time_interval=0.3,
#     output_directory = None,
#     video_directory = None,
#     ):

#     warnings.warn("Decrap write_elan_file_from_openface!")

#     run_status = []


#     filename_no_ext = os.path.basename(csv_filepath).split(".")[0]
#     directory = os.path.dirname(csv_filepath)
    
#     datafile = pd.read_csv(csv_filepath,skipinitialspace=True )
#     #datafile = exploface.extraction.generate_emotions_from_AU(datafile)
    
#     # These will be the column names of the action units and the emotions
#     columns = [c for c in datafile.columns if "_c" in c]#[c for c in datafile.columns if "AU" in c and "_c" in c]

#     if video_directory:
#         # If video_directory is given, the link in the elan file will point to a avi/mp4 video in the video_directory
#         rel_video_path = os.path.join( os.path.relpath(video_directory, output_directory), filename_no_ext )
#     elif output_directory:
#         # If only a output_directory is given, it is assumed that the avi or mp4 video is in the input directory
#         rel_video_path = os.path.join( os.path.relpath(directory, output_directory), filename_no_ext )
#         video_directory = directory
#     else:
#         # If none of these directories is given, it is assumed that the elan file is saved in the directory
#         # where an avi/mp4 video is present
#         rel_video_path = filename_no_ext
#         video_directory = directory

#     if os.path.isfile(os.path.join(video_directory, filename_no_ext)+".avi"): rel_video_path+=".avi"
#     elif os.path.isfile(os.path.join(video_directory, filename_no_ext)+".mp4"): rel_video_path+=".mp4"
#     elif os.path.isfile(os.path.join(video_directory, filename_no_ext)+".mpeg"): rel_video_path+=".mpeg"
#     else: 
#         warnings.warn("No video file found for the elan file({}), we searched in {} for avi and mp4 files".format(csv_filepath, video_directory))
#         rel_video_path = "video_not_found"
        
#     # Create an elan document
#     ed = elanwriter.ElanDoc(rel_video_path)

#     # First print a tier to indicate the confidence of openface
#     times = exploface.extraction.get_activation_times(datafile, "confidence", threshold=0.95, method=threshold_method, 
#                                         smooth_over_time_interval=smooth_over_time_interval,
#                                         inverse_threshold = True)
#     for i in range(len(times)):
#         ed.add_annotation((1000*times[i][0], 1000*times[i][1]), "<95%", tier_name="Confidence")
#     if len(times)==0:
#         ed.add_annotation((0,0), "", tier_name="Confidence")
        
#     # Now walk over all the action units & emotions and add them to the elan file
#     for c in columns:
#         times = exploface.extraction.get_activation_times(datafile, c, threshold=0.95, method=threshold_method, 
#                                            smooth_over_time_interval=smooth_over_time_interval)
        
#         c_intensity = c.replace("_c", "_r")
#         if c_intensity in datafile.columns:
#             df = exploface.extraction.get_activation_dataframe(datafile, 
#                                                 feature_detected = c, feature_intensity = c_intensity,
#                                                 intensity_threshold = intensity_threshold,
#                                                 smooth_over_time_interval=smooth_over_time_interval)
            
           
#             for i in range(len(df)):
#                 start = df["start"][i]
#                 end = df["end"][i]
#                 #label =  str(round(df["duration"][i],2))+" sec, "
#                 label = "("+str(round(df["mean_intensity"][i],2))+"/5)"+" +/- "
#                 label += str(round(df["std_intensity"][i],2))

#                 #print(start, end, label)

#                 ed.add_annotation((1000*start, 1000*end), label, tier_name=c)
#             if len(times)==0:
#                 ed.add_annotation((0,0), c, tier_name=c)
                
#         else:
#             run_status.append("No intensity for "+c)
    
#     # Write out the elan file
#     print("Output???")
#     if output_directory:
#         print("1")
#         ed.write(os.path.join(output_directory, filename_no_ext+".eaf"))
#     else:
#         print("2",os.path.join(directory, filename_no_ext+".eaf"))
#         ed.write(os.path.join(directory, filename_no_ext+".eaf"))

#     return run_status


