#!/usr/bin/pythonw
# -*-coding:Utf-8 -*

import subprocess
import os
import sys
import numpy as np

import sources.path as path
import sources.inout as inout
import sources.insar as insar

#####################################################################################
#######   Numerical solver for elasticity                                     #######
#######       inputs: mesh (string): mesh of the shape                        #######
#######               u (string): output elastic displacement                 #######
#####################################################################################

def elasticity(mesh,u) :
  """Solve elasticity problem on mesh file and store in in u file"""
  # Set information in exchange file
  inout.setAtt(file=path.EXCHFILE,attname="MeshName",attval=mesh)
  inout.setAtt(file=path.EXCHFILE,attname="DispName",attval=u)
  
  # Call to FreeFem
  log = open(path.LOGFILE,'a')

  proc = subprocess.Popen(["{FreeFem} {elasticity} > /dev/null 2>&1".format(FreeFem=path.FREEFEM,elasticity=path.FFELAS)],shell=True,stdout=log)
  proc.wait()

  log.close()
  
  return proc

  if ( proc.returncode != 0 ) :
    print("Error in numerical solver; abort. OOO")
    print(proc.returncode)
    
#####################################################################################
#####################################################################################

#####################################################################################
#######   Calculate elastic compliance                                        #######
#######       inputs: mesh (string): mesh of the shape                        #######
#######               u (string): output elastic displacement                 #######
#####################################################################################

def compliance(mesh,u) :
  
  # Set information in exchange file
  inout.setAtt(file=path.EXCHFILE,attname="MeshName",attval=mesh)
  inout.setAtt(file=path.EXCHFILE,attname="DispName",attval=u)

  # Call to FreeFem
  proc = subprocess.Popen(["{FreeFem} {compliance} > /dev/null 2>&1".format(FreeFem=path.FREEFEM,compliance=path.FFCPLY)],shell=True)
  proc.wait()
  
  if ( proc.returncode != 0 ) :
    print("Error in compliance calculation; abort.")
    print(proc.returncode)
  
  [cply] = inout.getrAtt(file=path.EXCHFILE,attname="Compliance")
  
  return cply



#####################################################################################
#######   Computation of the adjoint state for the ERROR functional          #######
#######       inputs: mesh (string): mesh of the shape                        #######
#######               u (string): input elastic displacement                 #######
#######               p (string): output adjoint state                       #######
#####################################################################################

def adjoint(mesh,u,p) :
  
  # Set information in exchange file
  inout.setAtt(file=path.EXCHFILE,attname="MeshName",attval=mesh)
  inout.setAtt(file=path.EXCHFILE,attname="DispName",attval=u)
  inout.setAtt(file=path.EXCHFILE,attname="AdjName",attval=p)
  
  # Call to FreeFem
  proc = subprocess.Popen(["{FreeFem} {adjoint} > /dev/null 2>&1".format(FreeFem=path.FREEFEM,adjoint=path.FFADJ)],shell=True)
  proc.wait()

  if ( proc.returncode != 0 ) :
    print("Error in numerical solver for adjoint equation; abort.")
    print(proc.returncode)
    
#####################################################################################
#######   Calculate error data-model                                        #######
#######       inputs: mesh (string): mesh of the shape                        #######
#######               u (string): output elastic displacement                 #######
#####################################################################################

def error(mesh,u) :
  
  # Set information in exchange file
  inout.setAtt(file=path.EXCHFILE,attname="MeshName",attval=mesh)
  inout.setAtt(file=path.EXCHFILE,attname="DispName",attval=u)
  
  
  if path.ERRMOD == 2 : # interpolation of LOS disp at mesh nodes
      insar.lossol(path.TCK1, mesh, path.LOS1)
      insar.lossol(path.TCK2, mesh, path.LOS2)
  elif path.ERRMOD == 0 :
      inout.setAtt(file=path.EXCHFILE,attname="OutAna",attval=path.OUTANA)
      
  
  print(f"Computing error file {path.FFERR}")
  # Call to FreeFem
  proc = subprocess.Popen(["{FreeFem} {error} > /dev/null 2>&1".format(FreeFem=path.FREEFEM,error=path.FFERR)],shell=True)
  proc.wait()
  
  if ( proc.returncode != 0 ) :
    print("Error in error calculation; abort.")
    print(proc.returncode)
  
  [err] = inout.getrAtt(file=path.EXCHFILE,attname="Error")
  
  return err



#####################################################################################
#####################################################################################

#####################################################################################
#######   Calculate volume                                                    #######
#######       input: mesh (string): mesh of the shape                         #######
#####################################################################################

def volume(mesh) :
  
  # Set information in exchange file
  inout.setAtt(file=path.EXCHFILE,attname="MeshName",attval=mesh)

  # Call to FreeFem
  proc = subprocess.Popen(["{FreeFem} {volume} > /dev/null 2>&1".format(FreeFem=path.FREEFEM,volume=path.FFVOL)],shell=True)
  proc.wait()
  
  if ( proc.returncode != 0 ) :
    print("Error in compliance calculation; abort.")
    print(proc.returncode)
  
  [vol] = inout.getrAtt(file=path.EXCHFILE,attname="Volume")
  
  return vol



#####################################################################################
#######   Calculate volume                                                    #######
#######       input: mesh (string): mesh of the shape                         #######
#####################################################################################

def stats(mesh) :
  
  # Set information in exchange file
  inout.setAtt(file=path.EXCHFILE,attname="MeshName",attval=mesh)

  # Call to FreeFem
  proc = subprocess.Popen(["{FreeFem} {stats} > /dev/null 2>&1".format(FreeFem=path.FREEFEM,stats=path.FFSTATS)],shell=True)
  proc.wait()
  
  if ( proc.returncode != 0 ) :
    print("Error in stats calculation; abort.")
    raise Exception("Error in calculung geometrical statisitics (no source ?)")
    print(proc.returncode)
  
  [vol] = inout.getrAtt(file=path.EXCHFILE,attname="Volume")
  [barx] = inout.getrAtt(file=path.EXCHFILE,attname="Barx")
  [bary] = inout.getrAtt(file=path.EXCHFILE,attname="Bary")
  [barz] = inout.getrAtt(file=path.EXCHFILE,attname="Barz")
  
  return vol,barx,bary,barz



#####################################################################################
#####################################################################################

#####################################################################################
#######   Calculate gradient of the compliance functional                     #######
#######       input:  mesh (string): mesh of the shape                        #######
#######               disp (string): solution of the elasticity system        #######
#######       output: grad (string): shape gradient of compliance             #######
#####################################################################################

def gradCp(mesh,disp,grad) :
  
  # Set information in exchange file
  inout.setAtt(file=path.EXCHFILE,attname="MeshName",attval=mesh)
  inout.setAtt(file=path.EXCHFILE,attname="DispName",attval=disp)
  inout.setAtt(file=path.EXCHFILE,attname="GradName",attval=grad)

  # Call to FreeFem
  proc = subprocess.Popen(["{FreeFem} {gradCp} > /dev/null 2>&1".format(FreeFem=path.FREEFEM,gradCp=path.FFGRADCP)],shell=True)
  proc.wait()
  
  if ( proc.returncode != 0 ) :
    print("Error in calculation of gradient of compliance; abort.")
    print(proc.returncode)
    
    
#####################################################################################
#####################################################################################

#####################################################################################
#######   Calculate gradient of the ERROR functional                         #######
#######       input:  mesh (string): mesh of the shape                        #######
#######               disp (string): solution of the elasticity system        #######
#######               adj (string):  solution of the adjoint system           #######
#######       output: grad (string): shape gradient of stress                 #######
#####################################################################################

def gradE(mesh,disp,adj,grad,phi) :
  
  # Set information in exchange file
  inout.setAtt(file=path.EXCHFILE,attname="MeshName",attval=mesh)
  inout.setAtt(file=path.EXCHFILE,attname="DispName",attval=disp)
  inout.setAtt(file=path.EXCHFILE,attname="AdjName",attval=adj)
  inout.setAtt(file=path.EXCHFILE,attname="GradEName",attval=grad)
  inout.setAtt(file=path.EXCHFILE,attname="PhiName",attval=phi)

  # Call to FreeFem
  proc = subprocess.Popen(["{FreeFem} {gradE} > /dev/null 2>&1".format(FreeFem=path.FREEFEM,gradE=path.FFGRADE)],shell=True)
  proc.wait()
  
  if ( proc.returncode != 0 ) :
    print("Error in calculation of gradient of ERROR; abort.")
    print(proc.returncode)
    
#####################################################################################

#####################################################################################
#######   Calculate gradient of the volume function                           #######
#######       input:  mesh (string): mesh of the shape                        #######
#######       output: grad (string): shape gradient of volume                 #######
#####################################################################################

def gradV(mesh,grad) :
  
  # Set information in exchange file
  inout.setAtt(file=path.EXCHFILE,attname="MeshName",attval=mesh)
  inout.setAtt(file=path.EXCHFILE,attname="GradName",attval=grad)

  # Call to FreeFem
  proc = subprocess.Popen(["{FreeFem} {gradV} > /dev/null 2>&1".format(FreeFem=path.FREEFEM,gradV=path.FFGRADV)],shell=True)
  proc.wait()
  
  if ( proc.returncode != 0 ) :
    print("Error in calculation of gradient of volume; abort.")
    print(proc.returncode)

#####################################################################################
#####################################################################################

#######################################################################################
#####             Calculation of the (normalized) descent direction               #####
#####      inputs :   mesh: (string for) mesh ;                                   #####
#####                 phi: (string for) ls function                               #####
#####                 gCp: (string for) gradient of Compliance                    #####
#####                 Cp: (real) value of Compliance                              #####
#####                 gV: (string for) gradient of Volume                         #####
#####                 vol: (real) value of volume                                 #####
#####      Output:    g: (string for) total gradient                              #####
#######################################################################################

def descent(mesh,phi,E,gE,g) :

  inout.setAtt(file=path.EXCHFILE,attname="MeshName",attval=mesh)
  inout.setAtt(file=path.EXCHFILE,attname="PhiName",attval=phi)
  inout.setAtt(file=path.EXCHFILE,attname="GradEName",attval=gE)
  inout.setAtt(file=path.EXCHFILE,attname="Error",attval=E)
  # inout.setAtt(file=path.EXCHFILE,attname="GradVolName",attval=gV)
  # inout.setAtt(file=path.EXCHFILE,attname="Volume",attval=vol)
  inout.setAtt(file=path.EXCHFILE,attname="GradName",attval=g)
      
  # Velocity extension - regularization via FreeFem
  proc = subprocess.Popen(["{FreeFem} {ffdescent} > /dev/null 2>&1".format(FreeFem=path.FREEFEM,ffdescent=path.FFDESCENT)],shell=True)
  proc.wait()
    
  if ( proc.returncode != 0 ) :
    print(proc.returncode)
    raise Exception("Error in calculation of descent direction; abort.")


#######################################################################################
#######################################################################################
