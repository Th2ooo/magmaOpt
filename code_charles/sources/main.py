#!/usr/bin/pythonw
# -*-coding:Utf-8 -*

import os
import sys
import numpy as np
import subprocess
import path
import inout
import mshtools
import lstools
import inigeom
import mechtools

###############################################################
##################      START PROGRAM    ######################
###############################################################

print("*************************************************")
print("********************* SO Demo *******************")
print("*************************************************")

# Initialize folders and exchange files
inout.iniWF()

# Test the links with external C libraries
# inout.testLib()

# Creation of the initial mesh
inigeom.iniGeom(path.step(0,"mesh"))

# Resolution of the state equation
mechtools.elasticity(path.step(0,"mesh"),path.step(0,"u.sol"))

# Calculation of the least-square difference between observations and predictions
newJ  = mechtools.LSdisc(path.step(0,"mesh"),path.step(0,"u.sol"))

print("*** Initialization: Discrepancy {}".format(newJ))

# Coefficient for time step ( descent direction is scaled with respect to mesh size)
coef = 0.02

# Main loop
# At the beginning of each iteration, are available:
#    - the mesh $\¢alT^n$ of $D$ associated to the current shape $\Omega^n$;
#    - the solution to the linear elasticity equation on $\Omega^n$ (at the nodes of $D$).
#    - The value of the objective
for it in range(0,path.MAXIT) :
  curmesh  = path.step(it,"mesh")
  newmesh  = path.step(it+1,"mesh")
  curphi   = path.step(it,"phi.sol")
  newphi   = path.step(it+1,"phi.sol")
  curu     = path.step(it,"u.sol")
  curp     = path.step(it,"p.sol")
  newu     = path.step(it+1,"u.sol")
  curJgrad = path.step(it,"J.grad.sol")
  curgrad  = path.step(it,"grad.sol")
  curJ     = newJ
  
  print("***************************************************")
  print("Iteration {}: Objective {}".format(it,curJ))
  print("***************************************************")
  
  # Print values in the path.HISTO file
  inout.printHisto(it,curJ)

  # Change value of tolerance after a certain number of iterations
  if ( it == 100 ) :
    path.TOL  = 0.005
    path.HMIN = 0.03

  # Generation of a level set function for $\Omega^n$ on $D$
  print("  Creation of a level set function")
  lstools.mshdist(curmesh,curphi)
   
  # Calculation of the adjoint state
  print("  Computation of the adjoint state ")
  mechtools.adjoint(curmesh,curu,curp)
    
  # Calculation of the gradient of objective
  print("  Computation of a descent direction")
  mechtools.gradJ(curmesh,curu,curp,curJgrad)
  
  # Calculation of a descent direction
  mechtools.descent(curmesh,curphi,curJgrad,curgrad)

  # Line search
  for k in range(0,path.MAXITLS) :
    print("  Line search k = {}".format(k))

    # Advection of the level set function and smoothing of the resulting LS function
    print("    Level Set advection")
    lstools.advect(curmesh,curphi,curgrad,coef,newphi)
    # lstools.regls(curmesh,newphi,newphi)

    # Creation of a mesh associated to the new shape
    print("    Local remeshing")
    retmmg = mshtools.mmg3d(curmesh,1,newphi,path.HMIN,path.HMAX,path.HAUSD,path.HGRAD,1,newmesh)

    if ( retmmg ) :
      # Resolution of the state equation on the new shape
      print("    Resolution of the linearized elasticity system")
      mechtools.elasticity(newmesh,newu)

      # Calculation of the new values of compliance and volume
      print("    Evaluation of the new merit")
      newJ  = mechtools.LSdisc(newmesh,newu)
    
    # Decision
    # Accept iteration: break and increase slightly the "time step"
    if ( retmmg and ( newJ < curJ + path.TOL*abs(curJ) ) or ( k == 2 ) or ( coef < path.MINCOEF ) ) :
      coef = min(path.MAXCOEF,1.1*coef)
      print("    Iteration {} - subiteration {} accepted\n".format(it,k))
      break
    # Reject iteration: go to start of line search with a decreased "time step"
    else :
      print("    Iteration {} - subiteration {} rejected".format(it,k))
      proc = subprocess.Popen(["rm {nmesh}".format(nmesh=newmesh)],shell=True)
      proc.wait()
      coef = max(path.MINCOEF,0.6*coef)

###############################################################
####################       END PROGRAM      ###################
###############################################################

print("*************************************************")
print("****************** End of SO Demo ***************")
print("*************************************************")
