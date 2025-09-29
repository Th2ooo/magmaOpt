#!/usr/bin/pythonw
# -*-coding:Utf-8 -*

import os
import sys
import numpy as np

# Paths to folders
BASE = "/home/th2o/Documents/Cours/magmaOpt_dev/magmaOpt/"
RES     = "./res/"       # Directory for results
VID     = "./vid/"       # Directory for outputting truncated meshes
PLOTS   = RES+"plots/"    # Directory to output the plots and animations 
TESTDIR = RES + "test/"  # Directory for test of libraries
SCRIPT  = "./sources/"   # Directory for sources
DATA    = "./data/"      # directory for data folder
RUNS = "./runs"       # directory for the outputs of the different runs

# Global parameters
REFDIR        = 1          # Reference for Dirichlet B.C (bottom)
REFNEU        = 10 # REFIS ou 9       # Reference for Neumann B.C. (source)
REFISO        = REFNEU      # Reference for the boundary edges of the shape (source)
REFUP         = 20     # Reference for upper surface where data-model error (target function) is computed 
REFINT        = 3    #3  # Reference of the interior domain !!!!!!!!! DONT CHANGE BC IT IS DEFAULT INTERIOR FOR MSHDIST
REFEXT        = 2     #2  # Reference of the exterior domain

# Physical constants
YOUNG = 10e9 ; #E
POISS = 0.25 ; #nu
PRESS = 2 ;  #Pressure change DP (source load)

fact = 10e3 #6e3
# Initial guess parameters
XS = 0. #x coordinate of the center
YS = 0.0 #y coordinate of the center
ZS = -0.3*fact #z coordinate of the center
REX = 0.1*fact #x semi-axe of intial ellispoidal source
REY = 0.2*fact #y semi-axe of intial ellispoidal source
REZ = 0.1*fact #z semi-axe of intial ellispoidal source



# Synthetic source parameters
XST = 0.3*fact
YST = 0.3*fact
DEPTH =  0.2*fact   ; #depth of source (>0)
RVRAI = 0.1*fact ; # radius of the target analytical spherical source



# Error type parameters
ERRMOD = 1  
""" 0 if error is computed with analytic solution, 
    1 if computed with numeric sol
    2 if computed with real data (bestE = null test)
"""
OUTANA = 0 #out analytic displacement



# Parameters of the mesh
XEXT          = 1.*fact #extent of domain in X direction
YEXT          = 1.*fact #extent of domain in X direction
ZEXT          = 1.*fact #extent of domain in X direction



MESHSIZ       = 0.05*fact #nominal size of thee mesh (used by initial mesher and as regularisation length)
HMIN          = 0.02*fact #minimum autorized element lenght
HMAX          = 0.05*fact #maximum authorized element length
HAUSD         = 0.007*fact  #mawimum authorized gap between ideal shape and its mesh nodes
HGRAD         = 1.8 #max rati allowed between 2 adjascent edges



# Other parameters of the shape opt algo
EPS           = 1e-10 # Precision parameter
EPSP          = 1e-20 # Precision parameter for packing
ALPHA         = 0.07 # Parameter for velocity extension - regularization
ALPHALS       = 0.01 # Parameter for regularization of LS function
MAXIT         = 100000   # Maximum number of iterations in the shape optimization process
MAXITLS       = 6   # Maximum number of iterations in the line search procedure
MAXCOEF       = 100 # Maximum allowed step between two iterations (in # * MESHSIZ)
MINCOEF       = 10 # Minimum allowed move between two iterations (in # * MESHSIZ)
TOL           = 0.001  # Tolerance for a slight increase in the ERROR


# TIMESTEP      = 2.0 # Coefficient for time step ( descent direction is scaled with respect to mesh size)


#INSAR PARAMETERS
TCK1 = DATA + "a33.txt"  #1st insar track
TCK2 = DATA + "d44.txt"  #2nd insar track
LOS1 = RES +"los1.sol"
LOS2 = RES +"los2.sol"
HEA1 = 347.1 *np.pi/180  #heading 1 (rad)
INC1 = 33.3 *np.pi/180   #inclinaison 1 (rad)
HEA2 = 189.7 *np.pi/180
INC2 = 44.7 *np.pi/180
ORMOD = [2529373,179745] #local origin of the model relatively to the InSAR track, ISN16
RAWTOLOS = lambda r : r*0.148*1e-3#speed (mm/yr) converted in displacement (mm), then in m


voldom = 1960000000000
volsrce = 4/3*np.pi*RVRAI**3
VTARG         =  (voldom-volsrce)/voldom    # Volume target




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
FFCPLY         = SCRIPT + "compliance.edp"
FFERR          = SCRIPT + f"error{ERRMOD}.edp" #error script (one script per error mod)
FFADJ          = SCRIPT + f"adjoint{ERRMOD}.edp"#adjoint state solving script (one script per error mod)
FFGRADE        = SCRIPT + "gradE.edp" # grad error script
FFVOL          = SCRIPT + "volume.edp"
FFSTATS          = SCRIPT + "stats.edp"
FFGRADV        = SCRIPT + "gradV.edp"
FFTRUNC        = SCRIPT + "truncvid.edp"







# Names of output and exchange files
DEFMMG       = "./DEFAULT.mmg3d"
DEFMSHD      = "./DEFAULT.mshdist"

EXCHFILE     = RES + "exch.data"
EXCHFILEVID  = VID + "exch.data"
LOGFILE      = RES + "log.data"
HISTO        = RES + "histo.data"
STEP         = RES + "step"
OBJDISP      = RES + "uobj.sol"
OBJMESH      = RES + "uobj.mesh"
TMPSOL       = "./res/temp.sol"
TESTMESH     = TESTDIR + "test.mesh"
TESTPHI      = TESTDIR + "test.phi.sol"
TESTSOL      = TESTDIR + "test.grad.sol"




# Shortcut for various file types
def step(n,typ) :
  return STEP + "." + str(n) + "." + typ
