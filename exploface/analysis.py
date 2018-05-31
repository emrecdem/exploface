
import pandas as pd
import numpy as np


def find_overlap(df1, df2, key1, key2, room):
    
    found = 0
    overlap = False
    overlap_start = []
    for i in range(len(df1[df1["au"]==key1])):
        start_original = df1[df1["au"]==key1].iloc[i]["start"] 
        end_original = df1[df1["au"]==key1].iloc[i]["end"] 

        start = start_original - room
        end = end_original + room

        #print(au, "i="+str(i))

        for j in range(len(df2[df2["au"]==key2])):
            start_human = df2[df2["au"]==key2].iloc[j]["start"]
            end_human = df2[df2["au"]==key2].iloc[j]["end"]

            #print("      ", "j="+str(j))

            if (start_human >= start and start_human <= end) or \
                (end_human >= start and end_human <= end) or \
                (start_human < start and end_human > end):
                overlap = True
                overlap_start.append(start_original)
                #print("      ", "overlap found", start, end, start_human, end_human) 
                break
            else:
                overlap = False

        if overlap:
            found += 1
        #else:
            #print("      ", "overlap not found", start, end)



            #if overlap: print(au, start_original, end_original, start_human, end_human)
    #print(found, len(example_file_ts[example_file_ts["au"]==au]))
    return found, len(df1[df1["au"]==key1]), overlap_start

def make_comparison_table(openface_files, openface_timestamp_files, human_FACS_files,\
                        output_file_path=None, human_FACS_min_intensity = 0, room=1,\
                        au_nrs = ["01", "02", "04", "05", "06", "07", "09", "10", "12", "14", "15",\
                         "20", "23", "26"],\
              ):
    #import exploface.analysis
    
    # Please refactor this :O
    openface_ts_files = openface_timestamp_files
    human_files = human_FACS_files
    
    data = {}
            #["01", "02", "04", "05", "06", "07", "09", "12", "14", "15", 
             # "20", "23", "26"] # 10?
    

    for au in au_nrs: data.update({au:{"#of": [], 
                                       "#hum": [], 
                                       "#heat": [], 
                                       "of-hum": [], 
                                       "hum-of": [], 
                                       "heat-of": [], 
                                       "heat-hum": [], 
                                       "skip": []}})

    #au = "AU12"
    #room = 10

    #from_openface_found_in_FACS =[]
    #from_FACS_found_in_openface = []

    key_pain = "pain_start"

    #cols = {"AU": [], "#of": [], "#hum": [], "#heat": [], "of-hum": [], "hum-of": [], "heat-of": [], "heat-hum": [], "skip": []}

    for vid_i in range(len(openface_files)):
        # read in data corresponding to the video
        # Openface results in original format
        openface_file = pd.read_csv(openface_files[vid_i],skipinitialspace=True )
        # Openface results in timestamp format
        openface_file_ts = pd.read_csv(openface_ts_files[vid_i],skipinitialspace=True )
        # Human facs results in timestamp format
        human_FACS_file = pd.read_csv(human_files[vid_i],skipinitialspace=True )
        
        human_FACS_file = human_FACS_file[(human_FACS_file["modifier"]>=human_FACS_min_intensity) | \
                                          (human_FACS_file["au"]=="heat_start") | \
                                          (human_FACS_file["au"]=="pain_start")]
        
        #print(os.path.basename(openface_files[vid_i]), 
        #      os.path.basename(openface_ts_files[vid_i]), 
        #      os.path.basename(human_files[vid_i]))


        for au_nr in au_nrs:
            au = "AU"+au_nr

            skip = get_quality_openface_au_detection(openface_file, int(au_nr))["always_detect_warning"]

            if skip:
                data[au_nr]["skip"].append(1)
                nr_openface_found = 0
            else:
                data[au_nr]["skip"].append(0)
                nr_openface_found = len(openface_file_ts[openface_file_ts["au"]==au])

            nr_human_found = len(human_FACS_file[human_FACS_file["au"]==au])
            nr_heat_found = len(human_FACS_file[human_FACS_file["au"]==key_pain])

            data[au_nr]["#of"].append(nr_openface_found)
            data[au_nr]["#hum"].append(nr_human_found)
            data[au_nr]["#heat"].append(nr_heat_found)

            # Openface - FACS
            if skip or nr_openface_found == 0:
                #nr_openface_also_found_in_human = 0
                data[au_nr]["of-hum"].append(np.nan)
            else:
                key1 = key2 = au
                res = find_overlap(openface_file_ts, human_FACS_file, 
                                                      key1, key2, room)
                nr_openface_also_found_in_human = res[0]

                data[au_nr]["of-hum"].append(nr_openface_also_found_in_human / nr_openface_found)

            # FACS - Openface
            if skip:
                data[au_nr]["hum-of"].append(0)
            elif nr_human_found == 0:
                #nr_FACS_also_found_in_openface = 1
                data[au_nr]["hum-of"].append(np.nan)
            else:
                key1 = key2 = au
                res = find_overlap(human_FACS_file, openface_file_ts, key1, key2, room)
                nr_FACS_also_found_in_openface = res[0]

                data[au_nr]["hum-of"].append(nr_FACS_also_found_in_openface / nr_human_found)

            # Openface - Pain
            if skip:
                #nr_heat_found_by_openface = 0
                data[au_nr]["heat-of"].append(np.nan)
            elif nr_heat_found == 0:
                #nr_heat_found_by_openface = 1
                data[au_nr]["heat-of"].append(1)
            else:
                res = find_overlap(human_FACS_file, openface_file_ts, key_pain, au, room)
                nr_heat_found_by_openface = res[0]

                data[au_nr]["heat-of"].append(nr_heat_found_by_openface / nr_heat_found)

            # HUMAN - Pain
            if nr_heat_found == 0:
                #nr_heat_found_by_openface = 1
                data[au_nr]["heat-hum"].append(1)
            else:
                res = find_overlap(human_FACS_file, human_FACS_file, key_pain, au, room)
                nr_heat_found_by_human = res[0]

                data[au_nr]["heat-hum"].append(nr_heat_found_by_human / nr_heat_found)
                
    ## Now start calculating the means
    data_mean = {"au": [], 
                 "#of": [], 
                 "#hum": [], 
                 "#heat": [], 
                 "of-hum": [], 
                 "hum-of": [], 
                 "heat-of": [], 
                 "heat-hum": [], 
                 "skip": []
                }
    for au_nr in au_nrs:

        data_mean["au"].append("AU"+str(au_nr))
        data_mean["#of"].append(str(round(np.nanmean( data[au_nr]["#of"] ),2))+"+/-"+\
                                str(round(np.nanstd( data[au_nr]["#of"] ),2)) )
        
        data_mean["#hum"].append(str(round(np.nanmean( data[au_nr]["#hum"] ),2))+"+/-"+\
                                 str(round(np.nanstd( data[au_nr]["#hum"] ),2))
                                )
        
        data_mean["#heat"].append(str(round(np.nanmean( data[au_nr]["#heat"] ),2) )+"+/-"+\
                                 str(round(np.nanstd( data[au_nr]["#heat"] ),2) )
                                 )
        
        data_mean["of-hum"].append(str(round(np.nanmean( data[au_nr]["of-hum"] ),2))+"+/-"+\
                                   str(round(np.nanstd( data[au_nr]["of-hum"] ),2))
                                  )
        
        data_mean["hum-of"].append(str(round(np.nanmean( data[au_nr]["hum-of"] ),2))+"+/-"+\
                                   str(round(np.nanstd( data[au_nr]["hum-of"] ),2))
                                  )
        data_mean["heat-of"].append(str(round(np.nanmean( data[au_nr]["heat-of"] ),2))+"+/-"+\
                                    str(round(np.nanstd( data[au_nr]["heat-of"] ),2))
                                   )
        
        data_mean["heat-hum"].append(str(round(np.nanmean( data[au_nr]["heat-hum"] ),2) )+"+/-"+\
                                     str(round(np.nanstd( data[au_nr]["heat-hum"] ),2))
                                    )
        
        data_mean["skip"].append(str(round(np.nanmean( data[au_nr]["skip"] ),2) )+"+/-"+\
                                 str(round(np.nanstd( data[au_nr]["skip"] ),2))
                                )
    res = pd.DataFrame(data_mean)
    res.set_index("au")
    
    if output_file_path:
        res.to_csv(output_file_path)
        
    return res

def get_quality_openface_au_detection(df, au_nr):
    
    warnings_openface_result = {"always_detect_warning": False}
    
    if int(au_nr) < 10: au_nr = "AU0"+str(au_nr)
    else: au_nr = "AU"+str(au_nr)
    
    au_continuous = au_nr+"_r"
    au_discrete = au_nr+"_c"

    # Calculate average noise
    



    # Calculate average level discrete
    #   Some discrete curves are just completely at 1. Probably because the AU seems to be
    #   active all the time for openface. This could be if people have certain kinds of
    #   idle faces or if the face orientation mimics an AU (e.g. looking down and lowering brows)
    if np.mean(df[au_discrete])>0.2:
        warnings_openface_result["always_detect_warning"] = True

    return warnings_openface_result