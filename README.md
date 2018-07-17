# exploface

Author:
Licence: add it!!

## Introducion
Exploface is a simple python package to work with the output of openface. Openface is a software to analyse faces in images and videos. Please see the website of the authors for more information on openface: https://github.com/TadasBaltrusaitis/OpenFace/wiki

This package works with the output files of openface (csv files). It does some basic inspection and statistics with the data. It also allows to convert the data to a format readable by Elan (a video annotation tool, https://tla.mpi.nl/tools/tla-tools/elan/). Further more it is able to convert the per camera frame format of openface to a format that lists start and end times of a detection.

## Installation
Installation from the commandline. Please follow the general guidelines for installation:
https://packaging.python.org/tutorials/installing-packages/
In the link above it is described how to install a package and use virtual environments. When you are in your virtual environment in staal exploface by typing: pip install exploface.

Test the installation by starting the python environment (type python in your commandline). And then test by running "import exploface". If this works, you are ready to do the tutorial.

## Tutorials
In the directory TUTORIALS you find tutorials on how to use exploface. 
* Tutorial 1: https://github.com/emrecdem/exploface/TUTORIALS/tutorial1.ipynb
