#!/usr/bin/pythonw
# -*-coding:Utf-8 -*


import sources.path as path
import subprocess
import os
import sys
import numpy as np
import sources.mechtools as mechtools
from pathlib import Path
##############################################################
######          Set the field attname in file          #######
##############################################################

def setAtt(file="none",attname="none",attval="none"):
  """ Set the value attval in the field attname of file """
  
  # Open file
  ff = open(file,"r")
  content = ff.read()
  contentl = content.lower()
  lst = content.split()
  lstl = contentl.split()
  ff.close()
  
  isfnd = 0
  # Travel file
  for i,elt in enumerate(lstl) :
    if elt == attname.lower() :
      isfnd = 1
      ind = i+1
      lst[ind] = str(attval)
      break

  # If attname has been found, rewrite file out of the updated list
  if isfnd :
    with open(file,"w") as ff :
      for i,elt in enumerate(lst) :
        ff.write(elt+"\n")
        if ( i % 2 == 1 ) :
            ff.write("\n")

  # If attname has not been found, append at the end of the file
  else :
    with open(file,"a") as ff :
      ff.write(attname+"\n"+str(attval)+"\n\n")

##############################################################
##############################################################

##############################################################
###########    Get real value associated to kwd    ###########
#####      npar = number of real parameters to obtain     ####
##############################################################

def getrAtt(file="none",attname="none",npar=1) :
  """ Get real value associated to keyword kwd in file """
  
  # Open file
  ff = open(file,"r")
  content = ff.read()
  content = content.lower()
  lst = content.split()
  ff.close()
  
  # Travel file
  rval = []
  for i,elt in enumerate(lst) :
    if elt == attname.lower() :
      for j in range(1,npar+1) :
        rval.append(float(lst[i+j]))

  return ( rval )

##############################################################
##############################################################

#######################################################################
######           Initialize folders and exchange files           ######
#######################################################################

def iniWF():

  # Create and clear ./res folder for results depending on the situation
  proc = subprocess.Popen(["mkdir -p {folder}".format(folder=path.RES)],shell=True)
  proc.wait()
  proc = subprocess.Popen(["rm -rf {folder}*".format(folder=path.RES)],shell=True)
  proc.wait()
  
  
  # Copy pah file for debugging and anlysis
  proc = subprocess.Popen([f"cp {path.SCRIPT}path.py {path.RES}"],shell=True)
  proc.wait()
  proc = subprocess.Popen([f"mv  {path.RES}path.py {path.RES}path.data"],shell=True)
  proc.wait()

  
  # Create and clear ./testdir folder for results depending on the situation
  proc = subprocess.Popen(["mkdir -p {folder}".format(folder=path.TESTDIR)],shell=True)
  proc.wait()
  proc = subprocess.Popen(["rm -rf {folder}*".format(folder=path.TESTDIR)],shell=True)
  proc.wait()
  
  # Create and clear ./testdir folder for results depending on the situation
  proc = subprocess.Popen(["mkdir -p {folder}".format(folder=path.PLOTS)],shell=True)
  proc.wait()
  proc = subprocess.Popen(["rm -rf {folder}*".format(folder=path.PLOTS)],shell=True)
  proc.wait()

  # Create exchange file
  ff = open(path.EXCHFILE,'w')
  ff.close()
  
  # Create log file
  ff = open(path.LOGFILE,'w')
  ff.close()
  
  # Create histo file
  ff = open(path.HISTO,'w')
  ff.close()

  # Create DEFAULT.mshdist file: to make sure the level set is computed from the good interior
  ff = open(path.DEFMSHD,'w')
  ff.write(f"InteriorDomains\n1\n\n{path.REFINT}")
  ff.close()
  
  
  # Create DEFAULT.mmg3d file: for local refining of the uper surface
  if path.FINEUP :
      ff = open(path.DEFMMG,'w')
      ff.write(f"Parameters\n1\n\n{path.REFUP} Triangles {path.HAUSD} {path.MESHSIZ} {path.HMIN}")
      ff.close()
      
  
  # Add global information (e.g. about Dirichlet and Neumann boundaries)
  setAtt(file=path.EXCHFILE,attname="Dirichlet",attval=path.REFDIR)
  setAtt(file=path.EXCHFILE,attname="Neumann",attval=path.REFNEU)
  setAtt(file=path.EXCHFILE,attname="Refup",attval=path.REFUP)

  setAtt(file=path.EXCHFILE,attname="Regularization",attval=path.ALPHA)
  setAtt(file=path.EXCHFILE,attname="ReferenceBnd",attval=path.REFISO)
  setAtt(file=path.EXCHFILE,attname="Refint",attval=path.REFINT)
  setAtt(file=path.EXCHFILE,attname="Refext",attval=path.REFEXT)
  setAtt(file=path.EXCHFILE,attname="MeshSize",attval=path.MESHSIZ)
  
  # Model parameters
  setAtt(file=path.EXCHFILE,attname="Young",attval=path.YOUNG)
  setAtt(file=path.EXCHFILE,attname="Poisson",attval=path.POISS)
  setAtt(file=path.EXCHFILE,attname="Rvrai",attval=path.RTs[0][0])
  setAtt(file=path.EXCHFILE,attname="Xst",attval=path.XTs[0][0])
  setAtt(file=path.EXCHFILE,attname="Yst",attval=path.XTs[0][1])
  setAtt(file=path.EXCHFILE,attname="Depth",attval=-path.XTs[0][2])
  setAtt(file=path.EXCHFILE,attname="Pressure",attval=path.PRESS)
  
  # Objective files
  setAtt(file=path.EXCHFILE,attname="ObjDisp",attval=path.OBJDISP)
  setAtt(file=path.EXCHFILE,attname="ObjMesh",attval=path.OBJMESH)
  
  #  InSAR parameters for all input data files
  setAtt(file=path.EXCHFILE,attname="Ntracks",attval=path.NTCK)
  for i in range(path.NTCK) :
      setAtt(file=path.EXCHFILE,attname=f"Track{i}",attval=path.LOSS[i])
      setAtt(file=path.EXCHFILE,attname=f"Head{i}",attval=path.HEAS[i])
      setAtt(file=path.EXCHFILE,attname=f"Incl{i}",attval=path.INCS[i])
      setAtt(file=path.EXCHFILE,attname=f"Weight{i}",attval=path.WEIG[i])

      

##############################################################
##############################################################

##############################################################################
######        Test calls to external C libraries and softwares          ######
##############################################################################

def testLib():

  log = open(path.LOGFILE,'a')

  # Test call to FreeFem
  setAtt(file=path.EXCHFILE,attname="MeshName",attval=path.TESTMESH)
  setAtt(file=path.EXCHFILE,attname="PhiName",attval=path.TESTPHI)
  setAtt(file=path.EXCHFILE,attname="SolName",attval=path.TESTSOL)
  
  proc = subprocess.Popen(["{FreeFem} {test} > /dev/null 2>&1".format(FreeFem=path.FREEFEM,test=path.FFTEST)],shell=True)
  proc.wait()
  
  if ( proc.returncode == 0 ) :
    print("FreeFem installation working.")
  else :
    print("Problem with FreeFem installation.")
    exit()
      
  # Test call to mshdist
  oldsol = path.TESTMESH.replace('.mesh','') + ".sol"
  proc = subprocess.Popen(["mv {old} {new}".format(old=path.TESTPHI,new=oldsol)],shell=True,stdout=log)
  proc = subprocess.Popen(["{mshdist} {mesh} -fmm".format(mshdist=path.MSHDIST,mesh=path.TESTMESH)],shell=True,stdout=log)
  proc.wait()
  
  if ( proc.returncode == 0 ) :
    print("Mshdist installation working.")
  else :
    print("Problem with Mshdist installation.")
    exit()
  
  proc = subprocess.Popen(["mv {old} {new}".format(old=oldsol,new=path.TESTPHI)],shell=True,stdout=log)
  proc.wait()
    
  # Test call to advect
  proc = subprocess.Popen(["{adv} {msh} -s {vit} -c {chi} -dt {dt} -o {out} -nocfl".format(adv=path.ADVECT,msh=path.TESTMESH,vit=path.TESTSOL,chi=path.TESTPHI,dt=0.2,out=path.TESTPHI)],shell=True,stdout=log)
  proc.wait()
  
  if ( proc.returncode == 0 ) :
    print("Advect installation working.")
  else :
    print("Problem with Advect installation.")
    exit()
    
  # Test call to mmg
  proc = subprocess.Popen(["{mmg} {msh} -ls -sol {phi} -hmin 0.007 -hmax 0.05 -hausd 0.005 -hgrad 1.3".format(mmg=path.MMG3D,msh=path.TESTMESH,phi=path.TESTPHI)],shell=True,stdout=log)
  proc.wait()
  
  if ( proc.returncode == 0 ) :
    print("Mmg installation working.")
  else :
    print("Problem with Mmg installation.")
    exit()

  # Test command line sed
  proc = subprocess.Popen(["sed 's/MeshVersionFormatted/MeshVersion/g' {SolName} > /dev/null 2>&1".format(SolName=path.TESTSOL)],shell=True)
  proc.wait()
  proc = subprocess.Popen(["sed 's/MeshVersion/MeshVersionFormatted/g' {SolName} > /dev/null 2>&1".format(SolName=path.TESTSOL)],shell=True)
  proc.wait()
  
  if ( proc.returncode == 0 ) :
    print("sed command line working.")
  else :
    print("Problem with sed command line.")
    exit()

  print("All external libraries working.")
  log.close()
    
##############################################################################
##############################################################################

#################################################################################
######        Fill history file with error value          ######
######            Inputs: it (int) number of the iteration                 ######
######                    Er (real) value of error                    ######
#################################################################################

def printHisto(*args):

  histo = open(path.HISTO,'a')
  char = ""
  for a in args :
      char += f"{a} "
  print(char,file=histo)
  histo.close()




def recomp_histo() :
    """
    Function to recompute the histo.data file

    Parameters
    ----------
    resdir : TYPE, optional
        DESCRIPTION. The default is path.RES.

    Returns
    -------
    None.

    """
    resdir = Path(path.RES)
    oldhist = np.genfromtxt(resdir/"histo.data",delimiter=" ")
    nit = oldhist.shape[0] #number of iteration
    newhist = np.zeros(oldhist.shape)
    
    for it in range(0,nit) :
        print("it",it)
        curmesh = path.step(it,"mesh")
        curu    = path.step(it,"u.sol")
        
        #Compute stats of the current domain
        vol,barx,bary,barz = mechtools.stats(curmesh)
        
        # xompute current error
        curE = mechtools.error(curmesh,curu)


        # get old coef state
        coef = oldhist[it,3]
        
        # save new values
        newhist[it,:] = (it,curE,vol,coef,barx,bary,barz)
        
 
    np.savetxt(resdir/"histo.data",newhist,delimiter=" ", fmt='%.6e')

      
