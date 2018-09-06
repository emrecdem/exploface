
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def plot_action_units(csv_path, au_names, legend=True, show=True, filename=False):
	df = pd.read_csv(csv_path,skipinitialspace=True)

	if isinstance(au_names, str):
		au_names = [au_names]

	for au in au_names:
		if au in df:
			plt.plot(df["timestamp"], df[au], label=au)
		else:
			print(au+" not found in the data")
	
	plt.xlabel("Time (sec)")

	if legend:
		plt.legend()

	if isinstance(filename, str):
		plt.savefig(filename)

	if show:
		plt.show()
		plt.close()
	else:
		print("Edit the plot and use plt.show()")


