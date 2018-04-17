




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