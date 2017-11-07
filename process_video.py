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

	datafile["happy"] = (datafile["AU06_r"]+datafile["AU12_r"])/2
	datafile["surprise"]=(datafile["AU01_r"]+datafile["AU02_r"]+datafile["AU05_r"]+datafile["AU26_r"])/4
	datafile["sad"]=(datafile["AU01_r"]+datafile["AU04_r"]+datafile["AU15_r"])/3
	datafile["fear"]=(datafile["AU01_r"]+datafile["AU02_r"]+datafile["AU04_r"]+datafile["AU05_r"]+datafile["AU07_r"]+datafile["AU20_r"]+datafile["AU26_r"])/7 
	datafile["anger"]=(datafile["AU04_r"]+datafile["AU05_r"]+datafile["AU07_r"]+datafile["AU23_r"])/4
	datafile["disgust"]=(datafile["AU09_r"]+datafile["AU15_r"])/2

	datafile["happy_c"] = (datafile["AU06_c"]+datafile["AU12_c"])/2
	datafile["surprise_c"]=(datafile["AU01_c"]+datafile["AU02_c"]+datafile["AU05_c"]+datafile["AU26_c"])/4
	datafile["sad_c"]=(datafile["AU01_c"]+datafile["AU04_c"]+datafile["AU15_c"])/3
	datafile["fear_c"]=(datafile["AU01_c"]+datafile["AU02_c"]+datafile["AU04_c"]+datafile["AU05_c"]+datafile["AU07_c"]+datafile["AU20_c"]+datafile["AU26_c"])/7 
	datafile["anger_c"]=(datafile["AU04_c"]+datafile["AU05_c"]+datafile["AU07_c"]+datafile["AU23_c"])/4
	datafile["disgust_c"]=(datafile["AU09_c"]+datafile["AU15_c"])/2

	

