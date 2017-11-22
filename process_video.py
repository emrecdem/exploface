import sys
import os
import pandas as pd
import argparse
import matplotlib.pyplot as plt
from os.path import basename

import elanwriter
sys.path.append("./")
import process_AU

# INITIALISE PARSER
parser = argparse.ArgumentParser()
parser.add_argument("input", help="full path to the input video (mp4 format)")
parser.add_argument("-o", "--output", help="directory to which the output will be written")
parser.add_argument("-of", "--openfaceexe", help="full path to the FeatureExtraction.exe executable")
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
args = parser.parse_args()

verbose = args.verbose
inputpath = args.input
filename = basename(inputpath)
path = inputpath.split(filename)[0]

# ANALYSE ARGUMENTS
filename_no_ext = filename.split(".")[0]
if not args.output:
	outputpath = path
else:
	outputpath = args.output

if not args.openfaceexe:
	openface_feat_exe = os.path.join("OpenFace_0.2.3_win_x64", "FeatureExtraction.exe")
else:
	openface_feat_exe = args.openfaceexe
	if ".exe" not in openface_feat_exe:
		openface_feat_exe+=".exe"

# CHECK THE ARGUMENTS
if not os.path.isfile(inputpath):
	raise Exception("Input file and path do not exist:", inputpath)
if not os.path.isdir(outputpath):
	raise Exception("Output path does not exist:", outputpath)
if not os.path.isfile(openface_feat_exe):
	raise Exception("This openface feature extraction executable does not exist: ", openface_feat_exe)

if verbose:
	print("Input file: {}".format(inputpath))
	print("Output dir: {}".format(outputpath))
	print("Openface feature extraction executable: ", openface_feat_exe)

# RUN OPENFACE
if verbose: print("Starting openface feature extraction")
output_file_csv = os.path.join(path, filename_no_ext+".csv")
os.system(openface_feat_exe+" -f "+inputpath+" -of "+output_file_csv+"> output.temp")
if verbose: print("Finished openface feature extraction, reading in csv file")
datafile = pd.read_csv(output_file_csv,skipinitialspace=True )

# GENERATE emotions from the ActionUnits (AU)
datafile = process_AU.generateEmotionsFromAU(datafile)

# GENERATE time intervals for successful detection of the face and confidences
times_succes = process_AU.getSuccessTimes(datafile)
times_confident = process_AU.getUnConfidenceTimes(datafile, confidence_threshold = 0.8)
times_fail = process_AU.getFailTimes(datafile)

# PLOT SOME STATS
fig = plt.figure(figsize=(10,10))
plt.subplot(2,2,1)
plt.plot(datafile['timestamp'], datafile["confidence"], label="confidence")
y=0.99
for t in times_confident:
    plt.plot((t[0],t[1]), (y,y), color="red")
plt.xlabel("Time (sec)")
plt.ylabel("Confidence")
plt.legend()

plt.subplot(2,2,2)
plt.plot(datafile['timestamp'], datafile['pose_Tx'])
plt.xlabel("Time (sec)")
plt.ylabel("Side rotation head (degrees)")

fig.subplots_adjust(wspace=0.3)#, hspace=0)

plt.savefig(os.path.join(path, filename_no_ext+".pdf"))

plt.close()



# WRITE an Elan file with the success and confidence intervals
ed = elanwriter.ElanDoc(inputpath)
for i in range(len(times_confident)):
    ed.add_annotation((1000*times_confident[i][0], 1000*times_confident[i][1]), "<0.8", "Confidence")
for i in range(len(times_fail)):
    ed.add_annotation((1000*times_fail[i][0], 1000*times_fail[i][1]), "failure", "Detection failure")
ed.write(os.path.join(path, filename_no_ext+".eaf"))