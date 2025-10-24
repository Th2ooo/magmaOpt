#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 15:04:51 2024

@author: th2o
"""

import matplotlib.pyplot as plt
import meshio
import sources.path as path
import shutil
import numpy as np
import scipy as sc
from sources.utils import mesh_labmask


##GENERAL INSAR DARA


def los2sol(tckfile,meshfile,origin,outsol="",plot=False) :
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
    origin : tuple of 2 floats
        Choosen center of the mesh in geographical coordinates to shift the InsAR file. 
    outsol : string, optional
        Output .sol file after interpolation. If not provided, not saved
    plot : bool, optional
        To plot the interpolated data. The default is False.
        
    Returns
    -------
    Array of floats
        Localisations and interpolated data shape=(N,3).
    """
    
    print(f"Interpolating LOS from {tckfile} at mesh {meshfile} in {outsol}")
    
    ##Get  insar data
    tck = np.genfromtxt(tckfile)[:,:3]
    tck[:,:2] -= np.array(origin) 
    LOS = tck[:,2] #losdata

    ## Mesh data
    msh=meshio.read(meshfile)
    npt = msh.points.shape[0]
    mshloc = msh.points #coordinates of the mesh points
    # create mask to get all the points located on upper surface from cells
    mkup = mesh_labmask(msh,path.REFUP)
    
    ## Interpolation
    mshlos = sc.interpolate.griddata(
        tck[:,:2],LOS,mshloc[mkup][:,:2],
        method="nearest",
        fill_value=0.0)
    
    ## Saving to los file
    if outsol :
        los = np.full(npt, 0.0)
        los[mkup] = mshlos
        np.savetxt(outsol, los,
          header=f"MeshVersionFormatted 2\n\nDimension 3\n\nSolAtVertices\n{npt}\n1 1\n",
          comments="",
          fmt='%.15E')
    
    if plot: #plot to check
        fig,axs = plt.subplots(1,2,figsize=(10,4),layout="constrained")
        fig.suptitle(f"Track {tckfile}")
        ax = axs[0]
        c=ax.scatter(tck[:,0],tck[:,1],c=tck[:,2],marker=".",cmap="jet")
        ax.set_aspect('equal', adjustable='box')
        fig.colorbar(c,label="disp (m)")
        
        
        ax = axs[1]
        c=ax.scatter(mshloc[mkup][:,0],mshloc[mkup][:,1],c=mshlos,marker=".",cmap="jet")
        ax.set_aspect('equal', adjustable='box')
        fig.colorbar(c,label="disp (m)")
        fig.show()

    return np.column_stack((mshloc[:,:2][mkup],mshlos))



def los2k(tckfile,meshfile,origin,outsol="",fact=0.5,plot=False) :
    """
    Create the k function (1 where ther is data, 0 elsewhere) from the LOS 
    displacement data file (tckfile) on the nodes of meshfile
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
    fact : float, optional
        The factor by which meshzise is multiplied to get the radius around mesh points to search for data
    plot : bool, optional
        To plot the interpolated data. The default is False.

    """
    
    print(f"Computing k function from {tckfile} at mesh {meshfile} in {outsol}")
    ## Insar data
    tck = np.genfromtxt(tckfile)[:,:3]
    tck[:,:2] -= np.array(origin) 
    xylos = tck[:,:2] #coordinates of LOS points data

    ## Mesh data
    msh=meshio.read(meshfile)
    npt = msh.points.shape[0]
    mshloc = msh.points #coordinates of the mesh points
    # create mask to get all the points located on upper surface from cells
    mkup = mesh_labmask(msh,path.REFUP)
    xymshup = mshloc[mkup][:,:2]  #coordinates of upper surface mesh points

    ## KDtrees operations
    treelos = sc.spatial.KDTree(xylos)
    treemshup = sc.spatial.KDTree(xymshup)
    
    msh_neigh = treemshup.query_ball_tree(treelos,r=path.MESHSIZ*fact) #list of all data points within a distance meshsize/2 of mesh points
    k = np.array([int(bool(l)) for l in msh_neigh],dtype=int) #0 where no close data point (list empty), 1 elsewhere

    ## Saving k sol
    if outsol :
        kf = np.full(npt, 0.0)
        kf[mkup] = k
        np.savetxt(outsol, kf,
          header=f"MeshVersionFormatted 2\n\nDimension 3\n\nSolAtVertices\n{npt}\n1 1\n",
          comments="",
          fmt='%.15E')
        
    if plot: #plot to check
        fig,axs = plt.subplots(1,2,figsize=(10,4),layout="constrained")
        fig.suptitle(f"Track {tckfile}")
        ax = axs[0]
        c=ax.scatter(tck[:,0],tck[:,1],c=tck[:,2],marker=".",s=1,cmap="jet")
        ax.set_aspect('equal', adjustable='box')
        
        ax = axs[1]
        c=ax.scatter(xymshup[:,0],xymshup[:,1],c=k,marker=".",s=1,cmap="gray")
        ax.set_aspect('equal', adjustable='box')
        fig.colorbar(c,label="k")
        fig.show()

    return np.column_stack((xymshup,k))



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

            
    # Interpolating all insar tracks on the inital mesh, and computing theyre k functions
    for fk, flos,tck in zip(path.KS,path.LOSS,path.TCKS) :
        los2sol(tck, interp_mesh, locori,outsol=flos,plot=plot)
        los2k(tck, interp_mesh, locori,outsol=fk,plot=plot)



    
if __name__ =="__main__" :

    
    # los2sol(path.TCKS[0],path.step(0,"mesh"),path.LOSS[0],path.ORMOD, plot=1)
    init(1)

    # los2sol(path.TCKS[0],path.step(0,"mesh"),"res/atestsol.sol",path.ORMOD, plot=1)
    # msh = meshio.read(path.step(0,"mesh"))
    # los2k(path.TCKS[3],path.step(0,"mesh"),"res/ktest.sol",path.ORMOD, plot=1)
    
    
    pass