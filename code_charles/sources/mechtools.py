#!/usr/bin/pythonw
# -*-coding:Utf-8 -*

import subprocess
import inout
import os
import path
import sys
import numpy as np

#####################################################################################
#######   Numerical solver for elasticity                                     #######
#######       inputs: mesh (string): mesh of the shape                        #######
#######               u (string): output elastic displacement                 #######
#####################################################################################

def elasticity(mesh,u) :
  
  # Set information in exchange file
  inout.setAtt(file=path.EXCHFILE,attname="MeshName",attval=mesh)
  inout.setAtt(file=path.EXCHFILE,attname="DispName",attval=u)
  
  # Call to FreeFem
  proc = subprocess.Popen(["{FreeFem} {elasticity} > /dev/null 2>&1".format(FreeFem=path.FREEFEM,elasticity=path.FFELAS)],shell=True)
  proc.wait()

  if ( proc.returncode != 0 ) :
    print("Error in numerical solver; abort.")
    exit()
    
#####################################################################################
#####################################################################################

#####################################################################################
#######   Numerical solver for adjoint equation                               #######
#######       inputs: mesh (string): mesh of the shape                        #######
#######               u (string): elastic displacement                        #######
#######               p (string): output adjoint state                        #######
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
    print("Error in numerical solver; abort.")
    exit()
    
#####################################################################################
#####################################################################################

#####################################################################################
#######   Calculate difference between elastic displacement and target        #######
#######       inputs: mesh (string): mesh of the shape                        #######
#######               u (string): output elastic displacement                 #######
#######       output: J (float): value of the objective                       #######
#####################################################################################

def LSdisc(mesh,u) :
  
  # Set information in exchange file
  inout.setAtt(file=path.EXCHFILE,attname="MeshName",attval=mesh)
  inout.setAtt(file=path.EXCHFILE,attname="DispName",attval=u)
  
  # Call to FreeFem
  proc = subprocess.Popen(["{FreeFem} {LSdic} > /dev/null 2>&1".format(FreeFem=path.FREEFEM,LSdic=path.FFDISC)],shell=True)
  proc.wait()
  
  if ( proc.returncode != 0 ) :
    print("Error in calculation of objective; abort.")
    exit()
  
  [LSdisc] = inout.getrAtt(file=path.EXCHFILE,attname="LSdiscrepancy")
  
  return LSdisc

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
    exit()
  
  [vol] = inout.getrAtt(file=path.EXCHFILE,attname="Volume")
  
  return vol

#####################################################################################
#####################################################################################

#####################################################################################
#######   Calculate gradient of the objective functional                      #######
#######       input:  mesh (string): mesh of the shape                        #######
#######               disp (string): solution of the elasticity system        #######
#######               adj  (string): solution of the adjoint system           #######
#######       output: grad (string): shape gradient of compliance             #######
#####################################################################################

def gradJ(mesh,disp,adj,grad) :
  
  # Set information in exchange file
  inout.setAtt(file=path.EXCHFILE,attname="MeshName",attval=mesh)
  inout.setAtt(file=path.EXCHFILE,attname="DispName",attval=disp)
  inout.setAtt(file=path.EXCHFILE,attname="GradName",attval=grad)

  # Call to FreeFem
  proc = subprocess.Popen(["{FreeFem} {gradJ} > /dev/null 2>&1".format(FreeFem=path.FREEFEM,gradJ=path.FFGRADJ)],shell=True)
  proc.wait()
  
  if ( proc.returncode != 0 ) :
    print("Error in calculation of gradient of compliance; abort.")
    exit()
    
#####################################################################################
#####################################################################################


#######################################################################################
#####             Calculation of the (normalized) descent direction               #####
#####      inputs :   mesh: (string for) mesh ;                                   #####
#####                 phi: (string for) ls function                               #####
#####                 gJ: (string for) gradient of objective                      #####
#####      Output:    g: (string for) total gradient                              #####
#######################################################################################

def descent(mesh,phi,gJ,g) :

  inout.setAtt(file=path.EXCHFILE,attname="MeshName",attval=mesh)
  inout.setAtt(file=path.EXCHFILE,attname="PhiName",attval=phi)
  inout.setAtt(file=path.EXCHFILE,attname="GradJName",attval=gJ)
  inout.setAtt(file=path.EXCHFILE,attname="GradName",attval=g)
      
  # Velocity extension - regularization via FreeFem
  proc = subprocess.Popen(["{FreeFem} {ffdescent} > /dev/null 2>&1".format(FreeFem=path.FREEFEM,ffdescent=path.FFDESCENT)],shell=True)
  proc.wait()
    
  if ( proc.returncode != 0 ) :
    print("Error in calculation of descent direction; abort.")
    exit()

#######################################################################################
#######################################################################################
