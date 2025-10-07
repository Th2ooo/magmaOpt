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
import shutil
import numpy as np
import scipy as sc



##GENERAL INSAR DARA


def los2sol(tckfile,meshfile,outsol,origin, plot=False) :
    """
    Interpolate the LOS displacement data files of tckfile on the nodes of meshfile
    Save the result in sol format at outsol
    !!! The LOS displacement file coordinates has to be given in a cartesian coordinate system
    !!! if it's too slow, try to downsample the file before
    Parameters
    ----------
    tckfile : string
        LOS data file location. must be CSV-like formated, with X,Y,LOS format
    meshfile : string
        Meshfile location !! needs to be in .mesh format.
    outsol : string
        Output .sol file after interpolation.
    origin : tuple of 2 floats
        Choosen center of the mesh in geographical coordinates to shift the InsAR file. 
    plot : bool, optional
        To plot the interpolated data. The default is False.

    """
    
    print(f"Interpolating LOS from {tckfile} at mesh {meshfile} in {outsol}")
    ##Get raw insar data
    tck = np.genfromtxt(tckfile)[:,:3]
    # !!!! TOREMOVE below to stay general for any file
    tck[:,[1, 0]] = tck[:,[0, 1]] #swap columns to have lat lon format
    tck[:,:2]=WGS84ll_to_ISN16xy(tck[:,:2]) #conversion to isn16 system 
    tck[:,:2] -= np.array(origin) #shift to be centered at the desired originlocal origin of the model
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
        b= art.plot_simple(tck[:,:2],tck[:,2], cmap="turbo") #raw
        art.fig.colorbar(b)
        art.switch_ax()
        a=art.plot_simple(mshloc[mkup][:,:2], mshlos, cmap="turbo",vmin=np.min(mshlos)) #interpolated
        art.fig.colorbar(a)
    return mshloc[mkup]






def init(plot=False) :
    """
    Init the insar field sol files by creating an empty mesh and  interpolating the los data on it

    """
    
    # copying the initial mesh as the objective mesh to interpolate insar data
    interp_mesh = path.step(0,"mesh") #!!!! Maybe change to a custom mesh without source
    shutil.copy2(interp_mesh,path.OBJMESH)
    
    if not path.ORMOD : #if no specific local origin is specified, its the mean of all center of all tracks
        locori = np.array([0,0])
        for i,tck in enumerate(path.TCKS) :
            tck = np.genfromtxt(tck)[:,:3]
            Xc = (tck[:, 0].max()+tck[:, 0].min())/2
            Yc = (tck[:, 1].max()+tck[:, 1].min())/2
            locori += np.array([Xc,Yc])
        locori /= len(path.TCKS)
    else :
        locori = path.ORMOD

            
    # Interpolating all insar tracks on the inital mesh
    for flos,tck in zip(path.LOSS,path.TCKS) :
        los2sol(tck, interp_mesh, flos, locori,plot)


    
if __name__ =="__main__" :
    # HEA1 = (347.1+90) *np.pi/180  #heading 1 (rad)
    # INC1 = 33.3 *np.pi/180   #inclinaison 1 (rad)
    # a=LOS_set(HEA1, HEA1)
    # print(a(1,0,0))
    # print(a(0,1,0))
    # print(a(0,0,1))
    # a=los2sol(path.TCK1, path.step(1,"mesh"), path.LOS1,True)
    
    init()

