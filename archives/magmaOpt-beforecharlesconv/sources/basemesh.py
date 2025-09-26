#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 24 00:24:58 2024

@author: th2o
"""
import os
import gmsh 
import numpy as np
import subprocess


from sources.utils import Extent
import sources.mshtools as mshtools

import sources.path as path


def build_mesh(out,vizu=False,basic=True,verb=3) :
    """Build initial mesh with magma chamber
    verbosity=4 => normal gmsh verbosity"""
    ####Paramters
    xs = path.XS
    ys = path.YS
    zs = path.ZS

    rx = path.REX #semi axes ellipsoif
    ry = path.REY
    rz = path.REZ
    
    domex = Extent()
    domex.init_with_range(path.XEXT,path.YEXT,path.ZEXT)
    if not basic :
        domex.enlarge([10e3,10e3,10e3])
        
    
    ####Intialization
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 1)  # Use terminal output instead of GUI
    gmsh.option.setNumber("General.Verbosity", verb)
    gmsh.model.add("magma_source_flat")
    mod = gmsh.model
    occ = mod.occ
    msh = mod.mesh
    
    ####Geometry
    occ.addBox(domex.xmin, domex.ymin, domex.zmin,
               domex.xrange, domex.yrange, domex.zrange,tag=1)
    occ.addSphere(xs, ys, zs, 1,tag=2)
    occ.dilate([(3,2)],xs,ys,zs,rx,ry,rz)
    occ.cut([(3,1)],[(3,2)], removeTool=False) #cut the domain but keep interior of ellipse
    occ.synchronize()
    
    #retag with the correct labels according to sotuto
    # print(mod.getEntities())
    
    mod.setTag(2,12,path.REFDIR) #bottom surface = dirichlet boundary (blocked)
    mod.setTag(2,10,path.REFUP) #top surface = surface for error calculation
    mod.setTag(2,7,path.REFISO) #source surface = neumann surface = iso surface (loaded)
    
    
    mod.setTag(3,1,101) #interior of the domain = Tint
    mod.setTag(3,2,102) #interior of the source = Text
    mod.setTag(3,101,path.REFINT) #interior of the domain = Tint
    mod.setTag(3,102,path.REFEXT) #interior of the source = Text
    # print(mod.getEntities())
    
    ####Meshing
    if basic :
        msh.setSize(mod.getEntities(), path.MESHSIZ)
        
    else :
        inex = Extent() #extent of the fine meshed part
        inex.init_with_range(path.XEXT,path.YEXT,path.ZEXT)
        tagBox = msh.field.add("Box")
        msh.field.setNumber(tagBox, "VIn",path.MESHSIZ)
        msh.field.setNumber(tagBox, "VOut", 3e3)
        msh.field.setNumber(tagBox, "XMin", inex.xmin)
        msh.field.setNumber(tagBox, "XMax", inex.xmax)
        msh.field.setNumber(tagBox, "YMin", inex.ymin)
        msh.field.setNumber(tagBox, "YMax", inex.ymax)
        msh.field.setNumber(tagBox, "ZMin", inex.zmin)
        msh.field.setNumber(tagBox, "ZMax", inex.zmax)
        msh.field.setNumber(tagBox, "Thickness", 2e3)
        msh.field.setAsBackgroundMesh(tagBox)
        gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
        
    msh.generate()
        
    
    if vizu : #launch gmsh UI
        gmsh.fltk.run()
        
        
    ####Saving
    
    # Check if we can write to this location
    if os.access(os.path.dirname(out), os.W_OK):
        print('Mesh file acces ok')
        gmsh.write(out)
    else:
        print("No write permission in this directory!")

    
    
    # Close gmsh
    gmsh.finalize()
    
    
    
def inimsh(mesh,vizu=False,basic=True,verb=3) :
  
    
    build_mesh(mesh,vizu,basic,verb)

    # Call to mmg3d for remeshing the background mesh
    mshtools.mmg3d(mesh,0,None,path.HMIN,path.HMAX,path.HAUSD,path.HGRAD,1,mesh)
    log = open(path.LOGFILE,'a')

    proc = subprocess.Popen([f"{path.MMG3D} {mesh} -hmin {path.HMIN} -hmax {path.HMAX} -hausd {path.HAUSD} -hgrad {path.HGRAD} {mesh} -rmc -nosurf "],shell=True,stdout=log)
    proc.wait()
    log.close()
    if ( proc.returncode != 0 ) :
      return 0
    else :
      return 1
      
