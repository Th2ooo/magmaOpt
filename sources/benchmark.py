#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 25 13:15:21 2026

@author: th2o

Description: The purpose of this script is to benchmark the forward FEM model
using the exercises proposed by Crozier et al. 2023 (Understanding the drivers 
of volcano deformation through geodetic model verification and validation) at 
http://www.driversofvolcanodeformation.org/ . To run, the reference solutions
must be provided in the "data" folder.
"""
import sources.path as path
import sources.basemesh as basemesh
import sources.inout as inout
import sources.mechtools as mechtools
from sources.utils import mesh_labmask


import numpy as np
import time
import meshio
import scipy as sc
import matplotlib.pyplot as plt


SMALL_SIZE, MEDIUM_SIZE, BIGGER_SIZE = 18, 18, 30;
plt.rcParams.update({
    'font.family' : 'sans-serif' , 'font.size': MEDIUM_SIZE ,  'axes.titlesize' : MEDIUM_SIZE , 'axes.labelsize' : MEDIUM_SIZE + 2, 
    'xtick.labelsize' : MEDIUM_SIZE , 'ytick.labelsize' : MEDIUM_SIZE, 'legend.fontsize' : SMALL_SIZE + 1 , 'figure.max_open_warning' : 0,
    'figure.figsize' : (20, 10)
});



NRMSD = lambda u,ur : (np.sum((u-ur)**2,axis=0)/np.sum(ur**2,axis=0))**0.5 ## definition according to crozier 2023

def solve_problem(exo) :
    print(exo)
    meshf = path.TESTDIR+f"bench{exo['name']}.mesh"    
    dispf = path.TESTDIR+f"bench{exo['name']}.sol"

    st = time.time()
    basemesh.build_mesh(meshf,path.X0,path.R0,mmg=0,vizu=0,verb=3) #creating mesh of the solution
    mt = time.time()-st
    mechtools.elasticity(meshf,dispf)
    et = time.time()-st+mt
    
    print(f"Mesh buliding: {mt:.4f}s, Elasticity resolution: {et:.4f}s, Total: {et+mt:.4f}")
    
    ## Load reference solution
    refdat = np.genfromtxt(path.DATA+exo['reffile'],delimiter=",",skip_header=11,missing_values="NaN")
    xref = refdat[:,0] #x coordinates
    uref = refdat[:,1:4]
    
    xref3d = np.zeros((len(xref),3)) 
    xref3d[:,0] =xref #3dcoordinate array for interpolation 
    
    ## Load solution
    msh=meshio.read(meshf)
    mshloc = msh.points #coordinates of the mesh points
    print(f"Mesh stats : {msh.points.shape[0]} edges, {msh.cells[1].data.shape[0]} triangles , {msh.cells[2].data.shape[0]} tetras")
    # create mask to get all the points located on upper surface from cells
    mkup = mesh_labmask(msh,path.REFUP)
    mshloc = mshloc[mkup]
    umodfull = np.genfromtxt(dispf,skip_header=8,skip_footer=1)[mkup]
    
    # interpolate mesh data on ref coordinates
    umod = sc.interpolate.griddata(
            mshloc[:,:2],umodfull,xref3d[:,:2],
            method="cubic",
            fill_value=0.0) 
    
    np.savetxt(path.TESTDIR+f"magmaOpt_bench{exo['name']}.csv", np.hstack((xref[:,np.newaxis],umod,np.zeros((umod.shape[0],6)))),
        header="Théo Perrot\nInstititue of Earth Sicences \n N/A \n24/02/2026 \n1.1A\nNumerical\nN/A\nN/A\nN/A\nN/A",
        fmt='%.15E',
        delimiter=",",
        comments="")
    
    # plotting
    fig, axs = plt.subplots(1,3,figsize=(15,5))
    for i in range(3) :
        axs[i].plot(xref,uref[:,i],lw=5)
        axs[i].plot(xref,umod[:,i])
    print("NRMSD:",NRMSD(umod,uref))

    
    return xref,uref,umod,mt,et
    




## Setting the problem parameter at the Crozier et al. 2023 Exercise 1 value

exos = [{"name":"1A","reffile":"zhong1,25km.csv"},{"name":"1C","reffile":"zhong4km.csv"}] # problems files

RESULTS = []

G = 10e9 #PA
nu = 0.25
path.YOUNG = 2*G*(1+nu)
path.POISS = nu
path.PRESS = 10e6 #Pa



## Ex 1A
path.X0 = [0.,0.,-1.25e3]
path.R0 = [1e3]*3

# Solve problem on standard mesh
path.XEXT = 10e3
path.YEXT = 10e3
path.ZEXT = 10e3
path.MESHSIZ = 400
inout.iniWF() # update exchange parameters values
res = solve_problem(exos[0])
RESULTS += [res]

# Solve problem on fine mesh
path.XEXT = 15e3
path.YEXT = 15e3
path.ZEXT = 15e3
path.MESHSIZ = 200
inout.iniWF() # update exchange parameters values
res = solve_problem(exos[0])
RESULTS += [res]



## Ex 1C
path.X0 = [0.,0.,-4e3]
path.R0 = [1e3]*3

# Solve problem on standard mesh
path.XEXT = 10e3
path.YEXT = 10e3
path.ZEXT = 10e3
path.MESHSIZ = 400
inout.iniWF() # update exchange parameters values
res = solve_problem(exos[1])
RESULTS += [res]

# Solve problem on fine mesh
path.XEXT = 15e3
path.YEXT = 15e3
path.ZEXT = 15e3
path.MESHSIZ = 200
inout.iniWF() # update exchange parameters values
res = solve_problem(exos[1])
RESULTS += [res]






#%% Plots


fig, axs = plt.subplots(2,2,figsize=(15,10),layout="constrained")
count = 0
for i,exo in enumerate(exos) :
    for ii, (col) in enumerate(("red","purple")) :
        xref,uref,umod,mt,et = RESULTS[count]
        count += 1
        rs = NRMSD(umod,uref)
        
        for j,comp in enumerate((0,2)) :
            if ii == 0 :
                axs[i,j].plot(xref,uref[:,comp],lw=3,c="blue",ls="--")

            axs[i,j].plot(xref,umod[:,comp],
                          label=f"Meshing: {mt:.1f}s\nSolving: {et:.1f}s\nRes: {rs[comp]:.2f}",
                          c=col)
            if comp == 0 :
                axs[i,j].legend()

            
axs[0,0].set(ylabel="$u_x$ (m)",title="Ex 1A, $z/R=1.25$")
axs[0,1].set(ylabel="$u_y$ (m)",title="Ex 1A, $z/R=1.25$")
axs[1,0].set(ylabel="$u_x$ (m)",xlabel=("$X$ (m)"),title="Ex 1C, $z/R=4$")
axs[1,1].set(ylabel="$u_y$ (m)",xlabel=("$X$ (m)"),title="Ex 1C, $z/R=4$")

plt.savefig(path.PLOTS+"benchmark.pdf")

