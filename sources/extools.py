#!/usr/bin/pythonw
# -*-coding:Utf-8 -*

import sys
import subprocess
import math
import sources.path as path
import sources.inout as inout

""" 
Calls to external programs for
    -advection : advect
    -level set computation :  mshdist
    -level set remeshing : mmg3d
"""

#####################################################################################################
#######      Advect the L.S. function in ssol via the velocity svel; result in ssolout       ########
#######        Inputs: mesh: (string for) mesh;  phi: (string for) initial LS function      ########
#######                vel: (string for) velocity field; step: (real) final time;           ########
#######                           newphi: (string for) output L.S. function                 ########
#####################################################################################################

def advect(mesh,phi,vel,step,newphi) :

  log = open(path.LOGFILE,'a')

  # Advection by calling advect
  proc = subprocess.Popen(["{adv} {msh} -s {vit} -c {chi} -dt {dt} -o {out} -nocfl".format(adv=path.ADVECT,msh=mesh,vit=vel,chi=phi,dt=step,out=newphi)],shell=True,stdout=log)
  proc.wait()
  
  log.close()

#####################################################################################################
#####################################################################################################

##################################################################################################
###########       Create the signed distance function to the subdomain               #############
###########                  with reference path.REFINT                              #############
###########        mesh = mesh (string) ; phi = output distance (string)             #############
##################################################################################################

def mshdist(mesh,phi) :
  
  log = open(path.LOGFILE,'a')

  # Distancing with mshdist
  proc = subprocess.Popen(["{mshdist} {msh} -dom -fmm".format(mshdist=path.MSHDIST,msh=mesh)],shell=True,stdout=log)
  proc.wait()
  
  # Move output file to the desired location
  oldphi = mesh.replace('.mesh','') + ".sol"
  proc = subprocess.Popen(["mv {old} {new}".format(old=oldphi,new=phi)],shell=True,stdout=log)
  proc.wait()

  log.close()

##################################################################################################
##################################################################################################

##################################################################################################
#############             Laplacian smoothing of an input LS function                #############
#############             inputs:  mesh   (string): mesh of the shape                #############
#############                      phi    (string): level set function               #############
#############             output: phiout (string): regularized level set function    #############
##################################################################################################

def regls(mesh,phi,phiout) :
  
  # Set information in exchange file
  inout.setAtt(file=path.EXCHFILE,attname="MeshName",attval=mesh)
  inout.setAtt(file=path.EXCHFILE,attname="PhiName",attval=phi)
  inout.setAtt(file=path.EXCHFILE,attname="SolName",attval=phiout)

  # Call to FreeFem
  proc = subprocess.Popen(["{FreeFem} {regls} > /dev/null 2>&1".format(FreeFem=path.FREEFEM,regls=path.FFREGLS)],shell=True)
  proc.wait()
  
  if ( proc.returncode != 0 ) :
    print("Error in regularization of level set function; abort.")
    exit()
    
##################################################################################################
##################################################################################################



##############################################################################################################
######   Call to mmg3d                                                                                  ######
######   Inputs:   mesh (string) name of the mesh                                                       ######
######             ls   (int)  0 for standard remeshing mode, 1 for L.S. discretization mode            ######
######             phi  (string) name of the L.S. function                                              ######
######             hmin (real) minimum desired size of an element in the mesh                           ######
######             hmax (real) maximum desired size of an element in the mesh                           ######
######             hausd (real) geometric approximation parameter                                       ######
######             hgrad (real) mesh gradation parameter                                                ######
######             nr (int) 0 if identification of sharp angles, 1 if no identification                 ######
######   Output:   out (string) name of the output mesh                                                 ######
######   Return: 1 if remeshing successful, 0 otherwise
##############################################################################################################

def mmg3d(mesh,ls,phi,hmin,hmax,hausd,hgrad,nr,out) :
  
  log = open(path.LOGFILE,'a')
  
  if  ls :
    if nr :
      # print("nr+ls in remeshing")
      # !!!! option -optim added to avoid modyfing mesh size but may cause problems
      proc = subprocess.Popen(["{mmg} {mesh} -ls -sol {sol} -hmin {hmin} -hmax {hmax} -hausd {hausd} -hgrad {hgrad} -nr {res} -rmc".format(mmg=path.MMG3D,mesh=mesh,sol=phi,hmin=hmin,hmax=hmax,hausd=hausd,hgrad=hgrad,res=out)],shell=True,stdout=log)

      proc.wait()
    else :
      proc = subprocess.Popen(["{mmg} {mesh} -ls -sol {sol} -hmin {hmin} -hmax {hmax} -hausd {hausd} -hgrad {hgrad} {res} -rmc".format(mmg=path.MMG3D,mesh=mesh,sol=phi,hmin=hmin,hmax=hmax,hausd=hausd,hgrad=hgrad,res=out)],shell=True,stdout=log)
      proc.wait()
  else :
    if nr :
      proc = subprocess.Popen(["{mmg} {mesh} -hmin {hmin} -hmax {hmax} -hausd {hausd} -hgrad {hgrad} -nr {res} -rmc".format(mmg=path.MMG3D,mesh=mesh,sol=phi,hmin=hmin,hmax=hmax,hausd=hausd,hgrad=hgrad,res=out)],shell=True,stdout=log)
      proc.wait()
    else :
      proc = subprocess.Popen(["{mmg} {mesh} -hmin {hmin} -hmax {hmax} -hausd {hausd} -hgrad {hgrad} {res} -rmc".format(mmg=path.MMG3D,mesh=mesh,sol=phi,hmin=hmin,hmax=hmax,hausd=hausd,hgrad=hgrad,res=out)],shell=True,stdout=log)
      proc.wait()
  
  log.close()
  if ( proc.returncode != 0 ) :
    raise Exception("MMG remeshing failed !")
  else :
    return 1 

##############################################################################################################
##############################################################################################################
