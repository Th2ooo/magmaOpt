#!/usr/bin/pythonw
# -*-coding:Utf-8 -*

import os
import sys
import numpy as np




#### Files paths

BASE = "/home/th2o/Documents/Cours/magmaOpt_dev/magmaOpt/"
RES     = "./res/"       # Directory for results
PLOTS   = RES+"plots/"    # Directory to output the plots and animations 
TESTDIR = RES + "test/"  # Directory for test of libraries
SCRIPT  = "./sources/"   # Directory for sources
DATA    = "./data/"      # directory for data folder
RUNS = "./runs"       # directory for the outputs of the different runs


#### Labels

REFDIR        = 1          # Reference for Dirichlet B.C (bottom)
REFNEU        = 10 # REFIS ou 9       # Reference for Neumann B.C. (source)
REFISO        = REFNEU      # Reference for the boundary edges of the shape (source)
REFUP         = 20     # Reference for upper surface where data-model error (target function) is computed 
REFINT        = 3    #3  # Reference of the interior domain !!!!!!!!! DONT CHANGE BC IT IS DEFAULT INTERIOR FOR MSHDIST
REFEXT        = 2     #2  # Reference of the exterior domain



#### Physical problem paramaters

YOUNG = 25.4e9 ; #E (from sigmundsson 2024)
POISS = 0.257;   #nu (from sigmundsson 2024)
PRESS = 5e6 ;  #Pressure change DP (source load) (typical values at svarstengi)

fact = 10e3 #50e3 #6e3


# Initial guess parameters
XS = -0.3*fact #x coordinate of the center
YS = -0.3*fact #y coordinate of the center
ZS = -0.4*fact #z coordinate of the center
REX = 0.1*fact #x semi-axe of intial ellispoidal source
REY = 0.1*fact #y semi-axe of intial ellispoidal source
REZ = 0.1*fact #z semi-axe of intial ellispoidal source

# XS = 0. #x coordinate of the center
# YS = -0.0 #y coordinate of the center
# ZS = -4e3 #z coordinate of the center
# REX = 2e3 #x semi-axe of intial ellispoidal source
# REY = 2e3 #y semi-axe of intial ellispoidal source
# REZ = 1e3 #z semi-axe of intial ellispoidal source


# Objective source parameters (for ERRMOD 0 ou 1)
XST = 0.0*fact
YST = 0.0*fact
DEPTH =  0.5*fact   ; #depth of source (>0)
RVRAI = 0.1*fact ; # radius of the target analytical spherical source

# Extent of the simulated doain
XEXT          = 1.*fact #extent of domain in X direction
YEXT          = 1.*fact #extent of domain in X direction
ZEXT          = 1*fact #extent of domain in X direction



#### Meshing parameters
MESHSIZ       = 0.04*fact #nominal size of thee mesh (used by initial mesher and as regularisation length)
HMIN          = 0.01*fact #minimum autorized element lenght
HMAX          = 0.08*fact #maximum authorized element length
HAUSD         = 0.005*fact  #mawimum authorized gap between ideal shape and its mesh nodes

HGRAD         = 2 #max rati allowed between 2 adjascent edges
INHOM         = False #inhomogenous meshing for wider domains simulation
DILA          = 2 #dilataion parameter for the domain size if inhomogeneous meshing is selected



#### Optimization parameters

# Error type 
ERRMOD = 1  
""" 0 if error is computed with analytic solution, 
    1 if computed with numeric sol
    2 if computed with real data (bestE = null test)
    
"""
OUTANA = 0 #out analytic displacement
OBJDISP      = RES + "obj.sol" # path of the objective displacement field
OBJMESH      = RES + "obj.mesh" # path of the mesh associated with the objective field

# Other parameters of the shape opt algo
EPS           = 1e-10 # Precision parameter
EPSP          = 1e-20 # Precision parameter for packing

ALPHA         = 5*MESHSIZ # Parameter for velocity extension - regularization, few mesh elements (to textend gradient outside of REFISO)
MAXIT         = 100000   # Maximum number of iterations in the shape optimization process
MAXITLS       = 10   # Maximum number of iterations in the line search procedure
TOL           = 0.01  # Tolerance for a slight increase in the ERROR
MULTCOEF      = 1.2  #Multiplier for the step size (to accelerate convergence).1/MULTCOEF is applied if fail in reducing error
MINCOEF       = 0.01 # Minimum allowed move between two iterations (in # * MESHSIZ)
MAXCOEF       = 2 # Maximum allowed step between two iterations (in # * MESHSIZ)




#### InSAR parameters

TCKS = ["t16","t155","a33","d44","t26","t19"] #tck data files
TCKS = [DATA+tck+".csv" for tck in TCKS]
NTCK = len(TCKS) # number of tck files

LOSS = [OBJDISP.replace("sol",f"los{i}.sol") for i in range(len(TCKS))] #SOL files location after interpolation of the data location

HEAS = [347.4,191.7,347.1,189.7,349.6,195.1] #heading angles associated to the tracks
HEAS = [h*np.pi/180 for h in HEAS]
INCS = [34.6,37.6,33.3,44.7,43.2,22.7] #inclinaison angles associated to the tracks
INCS = [i*np.pi/180 for i in INCS]

WEIG = [1.]*6 #Weights given to the differents insar tracks
WEIG = np.array(WEIG)
WEIG = WEIG/np.sum(WEIG) # normalize the weights

ORMOD = (2529373,179745)  #local origin of the model relatively to the InSAR track coordinates. If not provided, the mean center of the tracks is automatically choosen


# tests with 1 track
NTCK = 1
TCKS = [TCKS[0]]
LOSS = [LOSS[0]]
HEAS = [HEAS[0]]
INCS = [INCS[0]]
WEIG = [WEIG[0]]




#### Scripts paths

# Call for the executables of external codes
FREEFEM = "FreeFem++"
MSHDIST = "mshdist"
ADVECT  = "/home/th2o/Softs/Advection/build/advect"
MMG3D   = "/home/th2o/Softs/mmg/build/bin/mmg3d_O3"
# Path to FreeFem scripts
FFTEST         = SCRIPT + "testFF.edp"
FFREGLS        = SCRIPT + "regls.edp"
FFDESCENT      = SCRIPT + "descent.edp"
FFINILS        = SCRIPT + "inils.edp"
FFELAS         = SCRIPT + "elasticity.edp"
FFERR          = SCRIPT + f"error{ERRMOD}.edp" #error script (one script per error mod)
FFADJ          = SCRIPT + f"adjoint{ERRMOD}.edp"#adjoint state solving script (one script per error mod)
FFGRADE        = SCRIPT + "gradE.edp" # grad error script
FFSTATS          = SCRIPT + "stats.edp"
FFTRUNC        = SCRIPT + "truncvid.edp"







# Names of output and exchange files
DEFMMG       = "./DEFAULT.mmg3d"
DEFMSHD      = "./DEFAULT.mshdist"

EXCHFILE     = RES + "exch.data"
LOGFILE      = RES + "log.data"
HISTO        = RES + "histo.data"
STEP         = RES + "step"
TMPSOL       = "./res/temp.sol"
TESTMESH     = TESTDIR + "test.mesh"
TESTPHI      = TESTDIR + "test.phi.sol"
TESTSOL      = TESTDIR + "test.grad.sol"




# Shortcut for various file types
def step(n,typ) :
  return STEP + "." + str(n) + "." + typ
