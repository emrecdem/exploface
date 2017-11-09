import os
import pandas as pd



input_dir = "DATA"
output_dir = "DATA"
files = ["video3"]
extension = ".mp4"

for f in files:
	path = os.path.join(input_dir, f+extension)
	path_out = os.path.join(output_dir, f+".csv")
	os.system("OpenFace_0.2.3_win_x64\\FeatureExtraction -f "+path+" -of "+path_out+"> output.temp")
	datafile = pd.read_csv(path_out,skipinitialspace=True )

	# datafile = datafile[datafile["success"]==1]

