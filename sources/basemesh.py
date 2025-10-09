#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 24 00:24:58 2024

@author: th2o
"""
import os
import gmsh 
import subprocess
import numpy as np

from sources.utils import Extent

import sources.path as path


def build_mesh(out,ext=[],psrc=[],rads=[],vizu=False,inhom=False,verb=3,debug=0) :
    """
    Build initial mesh with magma chamber

    Parameters
    ----------
    out : string
        output file where the mesh is written (has to be .mesh to be compatible with freefem/mmg)
    ext : list of floats, optional
        extent of the domain (X,Y,Z direction). If not provided, values from path are used.
    psrc : list of floats, optional
        position of the source (X,Y,Z direction). If not provided, values from path are used
    rads : list of floats, optional
        radii of the source (X,Y,Z direction). If not provided, values from path are used
    vizu : bool, optional
        Triigers gmsh gui to vizualize the mesh and model. The default is False.
    inhom : bool, optional
        inhom meshing mode = inhomogeneous, a coarser mesh is defined far from the source. The default is False = uniform meshsize.
    verb : bool, optional
        verboisity level of gmsh outputs. The default is 3.
    debug : bool, optional
        If true, plots and outputs additional steps for debugging purpose. The default is 0.

    Returns
    -------
    None.

    """
   
    ####Paramters
    if not ext :
        ext = [path.XEXT,path.YEXT,path.ZEXT]
    if not psrc :
        psrc = [path.XS,path.YS,path.ZS]
    if not rads :
        rads = [path.REX,path.REY,path.REZ]
    xs = psrc[0]
    ys = psrc[1]
    zs = psrc[2]

    rx = rads[0] #semi axes ellipsoif
    ry = rads[1]
    rz = rads[2]
    
    domex = Extent()
    domex.init_with_range(ext[0],ext[1],ext[2])
    if inhom :
        domex.dilate(path.DILA) #dilate the domain if inhom to add coars elements
        
    ####Intialization
    
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 1)  # Use terminal output instead of GUI
    gmsh.option.setNumber("General.Verbosity", verb)
    gmsh.model.add("magma_source_flat")
    
    mod = gmsh.model
    occ = mod.occ
    msh = mod.mesh
    
    ####Geometry
    
    # Intial dimTags for the box and the source
    volboxdt = (3,111)
    volsrcdt = (3,112)

    # add the box domain
    occ.addBox(domex.xmin, domex.ymin, domex.zmin,
               domex.xrange, domex.yrange, domex.zrange,tag=volboxdt[1])
    
    # add the source domain and stretch it to llatch the correct dimensionts
    occ.addSphere(xs, ys, zs, 1,tag=volsrcdt[1])
    occ.dilate([volsrcdt],xs,ys,zs,rx,ry,rz)
    
    if debug : 
        occ.synchronize()
        gmsh.fltk.run()

    # fragment the domain in 2 distincts subdomains, the interior of the source and the exterior
    (volsrcdt,volboxdt), _ = occ.fragment([volboxdt], [volsrcdt],removeObject=True, removeTool=True) 
    
    # remove anyduplicated entitires
    occ.removeAllDuplicates() 
    occ.synchronize()
    
    # get the identity of the generated surfaces
    surfsrcdt= mod.getBoundary([volsrcdt])[0]
    surfboxdts = mod.getBoundary([volboxdt])
    
    if debug :
        print("BBB",volsrcdt,volboxdt,surfsrcdt,surfboxdts)
        print("after generation",mod.getEntities())

    ## Retag with the correct labels according to pathfile    
    mod.setTag(2,12,path.REFDIR) #bottom surface = dirichlet boundary (blocked)
    mod.setTag(2,10,path.REFUP) #top surface = surface for error calculation
    mod.setTag(2,surfsrcdt[1],path.REFISO) #source surface = neumann surface = iso surface (loaded)
    mod.setTag(3,volboxdt[1],path.REFEXT) #interior of the domain = Text
    mod.setTag(3,volsrcdt[1],path.REFINT) #interior of the source = Tint

    if debug :
        print("FINAL tags",mod.getEntities())
        gmsh.fltk.run()



    
    ####Meshing

    if not inhom : #inhom uniform mesh size
        msh.setSize(mod.getEntities(), path.MESHSIZ)
        
    else :   #inhomogeneous mesh size  with extension of the domain to have wider domain
        # Disable options to prevent meshing from other source than mesh field
        gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
        
        inex = Extent() #extent of the fine meshed part, domain size
        inex.init_with_range(ext[0],ext[1],ext[2])
        
        # size and distance parameters
        hmin = path.MESHSIZ
        hmax = path.HMAX
        hgrad = path.HGRAD
        dmin = np.max(inex.ranges)*3**0.5/4 #fine meshed region is about the longest side of the domain's diagonal size -> max*sqrt(3)
        dmax = 2*(hmax-hmin)/hgrad+dmin #max distance to respect path.HGRAD/2 imposed in mmg
        print(f"Fine zone : dmin {dmin} dmax {dmax}")
        
        # Distance to the initial source field
        tagDist = msh.field.add("Distance") 
        msh.field.setNumbers(tagDist, "SurfacesList", [path.REFISO])
        msh.field.setNumber(tagDist, "Sampling", 100)
        
        
        # Threshold field, for a smooth increase in meshsize
        tagThres = msh.field.add("Threshold")
        msh.field.setNumber(tagThres, "Sigmoid", 1)
        msh.field.setNumber(tagThres, "InField", tagDist)
        msh.field.setNumber(tagThres, "SizeMin", hmin)
        msh.field.setNumber(tagThres, "SizeMax", hmax)
        msh.field.setNumber(tagThres, "DistMin", dmin)
        msh.field.setNumber(tagThres, "DistMax", dmax)
        msh.field.setNumber(tagThres, "StopAtDistMax", 0)
        
        # print("FIELD LIST2",msh.field.list())
        msh.field.setAsBackgroundMesh(tagThres) # set as meshsize
        
    # generate the mesh
    msh.generate()
    
    # remove the elements attached to the extra curve on the source generated by occ (creates labels problems after)
    undesired_dt = [(1,14),(0,14),(0,9)]
    for dt in undesired_dt : 
        msh.removeElements(dt[0],dt[1])
    msh.reclassifyNodes()
        
    # launch gmsh UI to check mesh and model
    if vizu or debug : 
        gmsh.fltk.run()
        
        
        
    ####Saving
    
    if os.access(os.path.dirname(out), os.W_OK):     # Check if we can write to this location
        print(f'Writing mesh in {out}')
        gmsh.write(out)
    else:
        print("No write permission in this directory!")
    
    
    # Close gmsh
    gmsh.finalize()

    

    
    
    
    
    
def inimsh(mesh,ext=[],psrc=[],rads=[],vizu=False,inhom=True,verb=3) :
  
    
    build_mesh(mesh,ext,psrc,rads,vizu,inhom,verb)
    print("GMSH meshing done")


    # rename temporaly the mesh for the remeshing
    tmpf = mesh.replace(".mesh",".tmp.mesh")
    os.rename(mesh, tmpf)
    
    # Call to mmg3d for remeshing the background mesh
    log = open(path.LOGFILE,'a')

    # !!! no -nr option to detect the ridges and keep them for the future
    proc = subprocess.Popen([f"{path.MMG3D} -in {tmpf} -hmin {path.HMIN} -hmax {path.HMAX} -hausd {path.HAUSD} -hgrad {path.HGRAD} -optim -out {tmpf} -rmc"],shell=True,stdout=log)

    proc.wait()
    log.close()
    
    if ( proc.returncode != 0 ) :
        raise Exception("MMG remeshing failed")
        return 0
    else :
        os.rename(tmpf,mesh) #rename to the correct name
        # print(os.listdir("./res/"))
        print("mmg remeshing done")
        return 1








      
if  __name__ == "__main__":
    # build_mesh("./res/test.mesh",inhom=1,debug=1)
    inimsh("./res/test1.mesh",vizu=1,inhom=1)
