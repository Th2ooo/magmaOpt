#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 15:04:51 2024

@author: th2o
"""
from sources.utils import *
from sources.geographer import *
from sources.artist import Artist
import meshio
import sources.path as path
import os
import numpy as np
import scipy as sc



##GENERAL INSAR DARA


def lossol(tckfile,meshfile,outsol,plot=False) :
    """Interpolate LOS disp of tckfile on the nodes of meshfile
    Save the result in sol format at outsol"""
    print(f"Interpolating LOS from {tckfile} at mesh {meshfile} in {outsol}")
    ##Get raw insar data
    tck = np.genfromtxt(tckfile)[:,:3]
    tck[:,[1, 0]] = tck[:,[0, 1]] #swap columns to have lat lon format
    tck[:,:2]=WGS84ll_to_ISN16xy(tck[:,:2]) #conversion to isn16 system
    tck[:,:2] -= path.ORMOD #shift to be centered at the local origin of the model
    tck[:,2] = path.RAWTOLOS(tck[:,2]) #conversion of speed (mm/yr) in displacement (m)
    
    ##Mesh data
    msh=meshio.read(meshfile)
    
    npt = msh.points.shape[0]
    mshloc = msh.points
    
    mkup = msh.point_data["medit:ref"]==path.REFUP #criterion with label
    # mkup = mshloc[:,2]==0.0 #criterion with alt
    
    
    mshlos = sc.interpolate.griddata(
        tck[:,:2],tck[:,2],mshloc[mkup][:,:2],
        method="linear",
        fill_value=0.0)
    
    los = np.full(npt, 0.0)
    los[mkup] = mshlos
    np.savetxt(outsol, los,
      header=f"MeshVersionFormatted 2\n\nDimension 3\n\nSolAtVertices\n{npt}\n1 1\n",
      comments="",
      fmt='%.15E')
    
    if plot: #plot to check
        art = Artist(1,2)
        b= art.plot_simple(tck[:,:2],tck[:,2], cmap="turbo") #interpolated
        art.fig.colorbar(b)
        art.switch_ax()
        a=art.plot_simple(mshloc[mkup][:,:2], mshlos, cmap="turbo",vmin=np.min(mshlos[mshlos!=-99])) #interpolated
        art.fig.colorbar(a)
    return mshloc[mkup]


# lossol(path.TCK1,path.step(0,"mesh"),path.LOS1)

if __name__ =="__main__" :
    HEA1 = (347.1+90) *np.pi/180  #heading 1 (rad)
    INC1 = 33.3 *np.pi/180   #inclinaison 1 (rad)
    a=LOS_set(HEA1, HEA1)
    print(a(1,0,0))
    print(a(0,1,0))
    print(a(0,0,1))
    a=lossol(path.TCK1, path.step(1,"mesh"), path.LOS1,True)

