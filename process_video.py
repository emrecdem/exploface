import sys
import os
import pandas as pd
import argparse
from os.path import basename

# INITIALISE PARSER
parser = argparse.ArgumentParser()
parser.add_argument("input", help="")
parser.add_argument("-o", "--output", help="")
parser.add_argument("-of", "--openfaceexe", help="Openface FeatureExtraction executable")
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
args = parser.parse_args()

verbose = args.verbose
inputpath = args.input
filename = basename(inputpath)
path = inputpath.split(filename)[0]

# ANALYSE ARGUMENTS
if not args.output:
	filename_no_ext = filename.split(".")[0]
	outputpath = os.path.join(path, filename_no_ext+".csv")
else:
	outputpath = args.output

if not args.openfaceexe:
	openface_feat_exe = os.path.join("OpenFace_0.2.3_win_x64", "FeatureExtraction.exe")
else:
	openface_feat_exe = args.openfaceexe
	if ".exe" not in openface_feat_exe:
		openface_feat_exe+=".exe"


if not os.path.isfile(inputpath):
	raise Exception("Input file and path do not exist:", inputpath)
if not os.path.isdir(path):
	raise Exception("Output path does not exist:", path)
if not os.path.isfile(openface_feat_exe):
	raise Exception("This openface feature extraction executable does not exist: ", openface_feat_exe)

if verbose:
	print("Input file: {}".format(inputpath))
	print("Output file: {}".format(outputpath))
	print("Openface feature extraction executable: ", openface_feat_exe)


if verbose: print("Starting openface feature extraction")
os.system(openface_feat_exe+" -f "+inputpath+" -of "+outputpath+"> output.temp")
if verbose: print("Finished openface feature extraction, reading in csv file")
datafile = pd.read_csv(outputpath,skipinitialspace=True )

