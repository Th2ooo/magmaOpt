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
PRESS = 1e6 ;  #Pressure change DP (source load) (typical values at svarstengi)

fact = 10e3 #50e3 #6e3

# Initial guess parameters
X0 = [0.,0,-3e3] #xyz coordinates of the center (it 0)
R0 = [2e3,2e3,2e3] #rx ry rz radii of the source
# X0 = np.array([0.0,0.0,-0.3])*fact #center
# R0 = np.array([0.1,0.1,0.1])*fact   #radius

# Objective / target source(s) parameters (for ERRMOD 0 ou 1) 
XTs = np.array([[0.3,0.3,-0.2]])*fact #centers
RTs = np.array([[0.1,0.1,0.1]])*fact   #radii

# Extent of the simulated doain
# XEXT          = 1.*fact #extent of domain in X direction
# YEXT          = 1.*fact #extent of domain in X direction
# ZEXT          = 1.*fact #extent of domain in X direction
XEXT          = 16e3 #extent of domain in X direction
YEXT          = 13e3 #extent of domain in X direction
ZEXT          = 9e3 #extent of domain in X direction



#### Meshing parameters
MESHSIZ       = 0.05*fact #nominal size of thee mesh (used by initial mesher and as regularisation length)
HMIN          = 0.01*fact #minimum autorized element lenght
HMAX          = 0.15*fact #maximum authorized element length
HAUSD         = 0.005*fact  #mawimum authorized gap between ideal shape and its mesh nodes

HGRAD         = 1.5 #max rati allowed between 2 adjascent edges
INHOM         = False #inhomogenous meshing for wider domains simulation
DILA          = 1.5 #dilataion parameter for the domain size if inhomogeneous meshing is selected
FINEUP        = True #implement refinement on  upper boundary with mmg 


#### Optimization parameters

# Error type 
ERRMOD = 2
""" 0 if error is computed with analytic solution, 
    1 if computed with numeric sol
    2 if computed with InSAR real data (bestE = null test)
    3 if computed with synthetic InSAR data (to debug)
    
"""
OUTANA = 0 #out analytic displacement
OBJDISP      = RES + "obj.sol" # path of the objective displacement field
OBJMESH      = RES + "obj.mesh" # path of the mesh associated with the objective field

# Other parameters of the shape opt algo
EPS           = 1e-10 # Precision parameter
EPSP          = 1e-20 # Precision parameter for packing

ALPHA         = 5*MESHSIZ # Parameter for velocity extension - regularization, few mesh elements (to textend gradient outside of REFISO)
MAXIT         = 10000   # Maximum number of iterations in the shape optimization process
MAXITLS       = 15   # Maximum number of iterations in the line search procedure
TOL           = 0.01  # Tolerance for a slight increase in the ERROR
MULTCOEF      = 1.2  #Multiplier for the step size (to accelerate convergence).1/MULTCOEF is applied if fail in reducing error
MINCOEF       = 0.005 # Minimum allowed move between two iterations (in # * MESHSIZ)
MAXCOEF       = 2. # Maximum allowed step between two iterations (in # * MESHSIZ)
INICOEF = MINCOEF # initial step size 



#### InSAR parameters

TCKS = ["t16","t155","a33","d44","t26","t19"] #tck data files
TCKS = [DATA+tck+".csv" for tck in TCKS]
NTCK = len(TCKS) # number of tck files



HEAS = [347.4,191.7,347.1,189.7,349.6,195.1] #heading angles associated to the tracks
HEAS = [h*np.pi/180 for h in HEAS]
INCS = [34.6,37.6,33.3,44.7,43.2,22.7] #inclinaison angles associated to the tracks
INCS = [i*np.pi/180 for i in INCS]



ORMOD = (2530000,180000)  #local origin of the model relatively to the InSAR track coordinates. If not provided, the mean center of the tracks is automatically choosen


# tests with 2 track
nums = [2,3]
NTCK = len(nums)
TCKS = [TCKS[i] for i in nums]
HEAS = [HEAS[i] for i in nums]
INCS = [INCS[i] for i in nums]

# WEIG = [1.]*NTCK #Weights given to the differents insar tracks
# WEIG =  np.array(WEIG)/np.sum(WEIG) # normalize the weights

WEIG = [0.01,0.01] #Weights given to the differents insar tracks

LOSS = [OBJDISP.replace("sol",f"los{i}.sol") for i in range(NTCK)] #SOL files location after interpolation of the data location


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
