import pandas as pd
import exploface.extraction
import numpy as np





def convert_bamberg_to_timestamp_format(dataframe):
    # Read in the excel file
    excel_file_content = dataframe
    # Select the columns we are interested in
    selected_content = excel_file_content[["Time_Relative_sf", "Duration_sf", "Behavior", "Event_Type", "Modifier_1"]]

    # The way the human FACS annotations are stored is in a way that the start and end of 
    # of an action unit is simply marked per line.
    stamps = []
    time_start, time_end, au, mod_start, mod_end = None, None, None, None, None
    
    # With i we walk over the rows of the dataframe
    for i in selected_content.index:
        # If a line contains a start of an AU we set the time and au ...
        if selected_content["Event_Type"][i] == "State start" and not time_start:
            time_start = selected_content["Time_Relative_sf"][i] 
            au = selected_content["Behavior"][i]
            mod_start = selected_content["Modifier_1"][i]
            #print(i, selected_content["Event_Type"][i], selected_content["Behavior"][i])

            # ... and then we start to walk over the rest of the rows to find the end 
            # marker of this specific entry
            j = i
            while not time_end:
                #print(j)
                # Then if the end marker is found it is stored
                if selected_content["Event_Type"][j] == "State stop" and selected_content["Behavior"][j] == au:
                    time_end = selected_content["Time_Relative_sf"][j]
                    mod_end = selected_content["Modifier_1"][i]
                j+=1

            # If the end marker is found all is added to the stamps list
            if time_end:
                au = "AU"+au.split("_")[0]
                stamps.append([time_start, time_end, au, mod_start, mod_end])
                time_start, time_end, au, mod_start, mod_end = None, None, None, None, None
            # If the end is not found, we have an incomplete entry in the FACS file
            else:
                print("END NOT FOUND FOR: ", i, time_start, au)
                
        elif selected_content["Event_Type"][i] == "State point":
            stamps.append([selected_content["Time_Relative_sf"][i], selected_content["Time_Relative_sf"][i]+0.5,\
                          selected_content["Behavior"][i], np.nan, np.nan])
            
            
    # We now put our results in a dataframe
    result = pd.DataFrame({"start": [ a for a,b,c,d,e in stamps ], 
                           "end": [ b for a,b,c,d,e in stamps ], 
                           "au":[ c for a,b,c,d,e in stamps ],
                           "modifier":[ d for a,b,c,d,e in stamps ]})

    #au_set = set(result["au"])
    #result
    #au_set
    #result[result["modifier"] != result["modifier"]]
    return result#[result["au"]=="AU43"]
