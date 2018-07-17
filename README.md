# exploface

Author:
Licence: add it!!

## Introducion
Exploface is a simple python package to work with the output of openface. Openface is a software to analyse faces in images and videos. Please see the website of the authors for more information on openface: https://github.com/TadasBaltrusaitis/OpenFace/wiki

This package works with the output files of openface (csv files). It does some basic inspection and statistics with the data. It also allows to convert the data to a format readable by Elan (a video annotation tool, https://tla.mpi.nl/tools/tla-tools/elan/). Further more it is able to convert the per camera frame format of openface to a format that lists start and end times of a detection.

## Installation (from the command-line)
1. Please follow the general guidelines for installing python packages and use a virtual environment:
https://packaging.python.org/tutorials/installing-packages/

2. When you are in your virtual environment install exploface by typing: 
```
pip install exploface
```

3. Test the installation by starting the python environment (type python in your commandline). And then test by running 
```
import exploface
```
If this works, you are ready to do the tutorial.

## Tutorials
In the directory TUTORIALS you find tutorials on how to use exploface. 
* Tutorial 1: https://github.com/emrecdem/exploface/blob/master/TUTORIALS/tutorial1.ipynb
