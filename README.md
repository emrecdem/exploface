# exploface

Author: B.L. de Vries (Netherlands eScience Center)

## Introducion
Exploface is a simple python package to work with the output of openface. Openface is a software to analyse faces in images and videos. Please see the website of the authors for more information on openface: https://github.com/TadasBaltrusaitis/OpenFace/wiki

This package works with the output files of openface (csv files). It does some basic inspection and statistics with the data. It also allows to convert the data to a format readable by Elan (a video annotation tool, https://tla.mpi.nl/tools/tla-tools/elan/). Further more it is able to convert the per camera frame format of openface to a format that lists start and end times of a detection.

## Installation (from the command-line)
1. Please follow the general guidelines for installing python packages and use a virtual environment:
	- Instructions for installing python packages with pip: https://packaging.python.org/tutorials/installing-packages/
	- You can also consider using conda to manage your environments: https://conda.io/docs/

2. When you are in your command-line console and optionally, your virtual environment, install exploface by typing: 
```
pip install exploface
```

3. Test the installation by starting the python shell (type ```python``` in your command-line). And then test by running 
```
import exploface
```
If this works, you are ready to do the tutorial.

## Tutorials
In the directory TUTORIALS you find tutorials on how to use exploface. 
* Tutorial 1: exploring openface csv files and using the exploface package
	- https://github.com/emrecdem/exploface/blob/master/TUTORIALS/tutorial1.ipynb
* Tutorial 2: underconstruction
	- https://github.com/emrecdem/exploface/blob/master/TUTORIALS/tutorial2.ipynb