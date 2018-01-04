import sys
import os
import pandas as pd
import argparse
import matplotlib.pyplot as plt
from os.path import basename

import elanwriter
sys.path.append("./")
import process_video

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


process_video.analyse_video(verbose, inputpath, filename, path, filename_no_ext, outputpath, openface_feat_exe)