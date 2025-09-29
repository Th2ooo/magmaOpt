#!/usr/bin/pythonw
# -*-coding:Utf-8 -*
#TO Run from spyder
import os
os.chdir("/home/th2o/Documents/Cours/magmaOpt_dev/magmaOpt")


import subprocess

import sys
import sources.path as path
import sources.insar as insar
import sources.mechtools as mechtools
import numpy as np
import pyvista as pv
import meshio
from sources.utils import *
from artist import *




print("**********************************************")
print("**********       Post-processing     *********")
print("**********************************************")


print("Retrieving best it")

# Load histogram
content = np.genfromtxt(path.HISTO,delimiter=" ")
nit = content.shape[0]
itl = content[:,0]
El = content[:,1]

bestit = np.argmin(El)

mechtools.elasticity(path.step(bestit,"mesh"),path.step(bestit,"u.sol"))
os.replace("u.vtu",f"best_it{bestit}.vtu")


## FUNCTIONS !!
##TODO : compute center of gravity of best it
##TODO : compute distance between 2 centers of gravity
##TODO : ball pivot algo for dist between meshes
##TODO : maybe slice sup part for redo same