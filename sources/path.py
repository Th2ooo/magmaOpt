#!/usr/bin/pythonw
# -*-coding:Utf-8 -*

import numpy as np

"""
Configuration file to set the parameters needed for the shape optimisation 
procedure.
"""


#### Files paths

RES     = "./res/"       # Directory for results
PLOTS   = RES+"plots/"   # Directory to output the plots and animations 
TESTDIR = RES + "test/"  # Directory for test of libraries
SCRIPT  = "./sources/"   # Directory for sources
DATA    = "./data/"      # directory for data folder
RUNS = "../runs"         # directory for the outputs of the different runs



#### Labels

REFDIR        = 1           # Reference for Dirichlet B.C (bottom)
REFNEU        = 10          # Reference for Neumann B.C. (source)
REFISO        = REFNEU      # Reference for the boundary Gamma (same as Neumann)
REFUP         = 20          # Reference for upper surface where data-model error (target function) is computed 
REFINT        = 3           # Reference of the interior domain Omega
REFEXT        = 2           # Reference of the exterior domain D\Omega



#### Physical problem paramaters

# Elastic quantities
YOUNG =  10e9          # Young modulus, Pa (from sigmundsson 2024)
POISS =  0.25          # Poison's ratio (from sigmundsson 2024)
PRESS = 2e6             # Pressure change DP (source load), Pa

# Initial guess Omega_0 parameters
X0 = [0.,0,-2e3]        # xyz coordinates of the shape center (it 0), m
R0 = [0.5e3,0.5e3,0.5e3]      # rx ry rz radii of the source, m

# Objective / target source(s) Omega* parameters (for ERRMOD 0 ou 1 only) 
XTs = np.array([[2e3,2e3,-2e3]])        #centers, m
RTs = np.array([[1e3,1e3,1e3]])             #radii, m

# Extent of the simulated doain
XEXT          = 10e3 #extent of domain in X direction, m
YEXT          = 10e3 #extent of domain in Y direction, m
ZEXT          = 10e3 #extent of domain in Z direction, m



#### Meshing parameters

MESHSIZ       = 500      # nominal size of thee mesh (used by initial mesher and as normalisation length), m
HMIN          = 20      # minimum autorized element lenght, m
HMAX          = 1000      # maximum authorized element length, m
HAUSD         = 50       # mawimum authorized gap between ideal shape and its mesh nodes, m

HGRAD         = 1.3      # max length ratio allowed between 2 adjascent edges
INHOM         = False    # inhomogenous meshing for wider domains simulation (works only for initial mesh, then mmg overides it)
DILA          = 1.5      # dilataion parameter for the domain element size if inhomogeneous meshing is selected
FINEUP        = True     # implement refinement on  upper boundary with mmg for more accurate error



#### Optimization parameters

# Restart
RESTARTIT = 0  # iteration where to restart the optimization, if it has been interupted. If 0, a new optimization is started and overwrites the former one

# Error type 
ERRMOD = 2
""" 0 if error is computed with analytic McTigue solution (BROKEN)
    1 if computed with numeric sol
    2 if computed with InSAR real data (bestE = null test)
    3 if computed with synthetic InSAR data (BROKEN)
"""

OBJDISP      = RES + "obj.sol"  # path of the objective displacement field
OBJMESH      = RES + "obj.mesh" # path of the mesh associated with the objective field

# Other parameters of the shape opt algo
EPS           = 1e-10      # Precision parameter in the computation of the descent
ALPHA         = MESHSIZ*5  # Velocity extension - regularization lenght, few mesh elements (to extend gradient outside of REFISO)
MAXIT         = 10000      # Maximum number of iterations in the shape optimization 
MAXITLS       = 10         # Maximum number of iterations in the line search procedure
TOL           = 0.02       # Tolerance for a slight increase in the ERROR
MULTCOEF      = 1.3        # Multiplier for the step size (to accelerate convergence).1/MULTCOEF is applied if fail in reducing error
MINCOEF       = 0.01      # Minimum allowed step size 
MAXCOEF       = 2.         # Maximum allowed step size between two iterations (in # * MESHSIZ)
INICOEF = 1                # initial step size 



#### InSAR parameters

TCKS = [DATA+tck+".csv" for tck in  ("t16","t155","a33","d44","t26","t19") ] # paths of insar tracks data files
NTCK = len(TCKS) # number of tck files
HEAS = [347.4,191.7,347.1,189.7,349.6,195.1] #heading angles associated to the tracks
HEAS = [h*np.pi/180 for h in HEAS]
INCS = [34.6,37.6,33.3,44.7,43.2,22.7] #inclinaison angles associated to the tracks
INCS = [i*np.pi/180 for i in INCS]
ORMOD = (2530000,179000)  #local origin of the model relatively to the InSAR track coordinates. If not provided, the mean center of the tracks is automatically choosen
WEIG = [1.]*NTCK #Weights given to the differents insar tracks
WEIG =  np.array(WEIG)/np.sum(WEIG) # normalize the weights
LOSS = [OBJDISP.replace("sol",f"los{i}.sol") for i in range(NTCK)] #SOL files path location after interpolation of the insar data on the mesh
KS = [OBJDISP.replace("sol",f"k{i}.sol") for i in range(NTCK)] 



#### Executables paths

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
TMPSOL       = RES + "temp.sol"
TESTMESH     = TESTDIR + "test.mesh"
TESTPHI      = TESTDIR + "test.phi.sol"
TESTSOL      = TESTDIR + "test.grad.sol"


# Shortcut to format the name of various file types
def step(n,typ) :
  return STEP + "." + str(n) + "." + typ
