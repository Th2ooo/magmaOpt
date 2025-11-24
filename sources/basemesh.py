#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GMSH based advanced mesh creation functions

Created on Fri May 24 00:24:58 2024

@author: Théo Perrot
"""
import os
import gmsh 
import meshio
import subprocess
import numpy as np

from sources.utils import Extent
import sources.path as path


def build_mesh(out,poss,rads,ext=[],inhom=False,rename=False,mmg=True,verb=3,debug=0,vizu=False) :
    """
    Build initial mesh with magma chamber

    Parameters
    ----------
    out : string
        output file where the mesh is written (has to be .mesh to be compatible with freefem/mmg)
    poss : list of list of floats
        position of the source (X,Y,Z direction)
    rads : list of list of floats
        radii of the source (X,Y,Z direction)
    ext : list of floats, optional
        extent of the domain (X,Y,Z direction), if not provided, values from the path are used
    vizu : bool, optional
        Triigers gmsh gui to vizualize the mesh and model. The default is False.
    inhom : bool, optional
        inhom meshing mode = inhomogeneous, a coarser mesh is defined far from the source. The default is False = uniform meshsize.
    mmg : bool, optional
        Post gmsh remeshing with mmg3d (prevent domains edge to be remeshed). default True
    verb : bool, optional
        verboisity level of gmsh outputs. The default is 3.
    debug : bool, optional
        If true, plots and outputs additional steps for debugging purpose. The default is 0.

    Returns
    -------
    None.

    """
   
    # COMMENTS ON GMSH
    # when saving to mesh formmat, physical groups are not preserved, only geometrical ones
    # possibiliy to rename with meshio
    
    
    ####Paramters
    if not ext :
        ext = [path.XEXT,path.YEXT,path.ZEXT]
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

    # add the box domain
    volboxdt = (3,111) # Intial dimTags for the box
    occ.addBox(domex.xmin, domex.ymin, domex.zmin,
               domex.xrange, domex.yrange, domex.zrange,tag=volboxdt[1])
    
    # add the sources domains and stretch it to match the correct dimensions
    volsrcdts = [] #intial dimtags for the sources
    for i,(pos,rad) in enumerate(zip(poss,rads)) :
        volsrcdts += [(3,1000+i)]
        xs,ys,zs = pos[0],pos[1],pos[2] # center positions
        rx,ry,rz = rad[0],rad[1],rad[2] #radii of ellispod
        occ.addSphere(xs, ys, zs, 1,tag=volsrcdts[i][1])
        occ.dilate([volsrcdts[i]],xs,ys,zs,rx,ry,rz)
    
    if debug : 
        occ.synchronize()
        gmsh.fltk.run()

    # fragment the domain in distincts subdomains, the interior of the source and the exterior 
    # fragment does "intersects all volumes in a conformal manner (without creating duplicate interfaces)" (gmsh doc)
    newdts, _ = occ.fragment([volboxdt], volsrcdts, removeObject=True, removeTool=True) 
    
    volboxdt = newdts[-1] # new box dt
    # remove anyduplicated entitires
    occ.removeAllDuplicates() 
    occ.synchronize()
    
    # get the identity of the generated surfaces
    surfsrcdts= mod.getBoundary(volsrcdts)
    surfboxdts = mod.getBoundary([volboxdt])
    
    if debug :
        print("BBB",volsrcdts,volboxdt,surfsrcdts,surfboxdts)
        print("after generation",mod.getEntities())
        

    ## Retag with the correct labels according to pathfile    
    mod.setTag(2,12,path.REFDIR) #bottom surface = dirichlet boundary (blocked)
    mod.setTag(2,10,path.REFUP) #top surface = surface for error calculation
    mod.setTag(3,volboxdt[1],path.REFEXT) #interior of the domain = Text
    if not rename :
        mod.setTag(3,volsrcdts[0][1],path.REFINT) #interior of the source = Tint
        mod.setTag(2,surfsrcdts[0][1],path.REFISO) #source surface = neumann surface = iso surface (loaded)
    
    
    # gmsh.option.setNumber("Mesh.SaveAll", 1)
    if debug :
        print("FINAL tags",mod.getEntities())
        gmsh.fltk.run()

    if not rename :
        # get the sources boundaries to delete them after mesh gen (lines and points useless)
        surfsrcdts= mod.getBoundary([(3,path.REFINT)])
        bad_ents = mod.getBoundary(surfsrcdts,oriented=False,recursive=False) #lines
        bad_ents += mod.getBoundary(surfsrcdts,oriented=False,recursive=True) #points

    
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
    
    if not rename :
        # remove the elements attached to the extra curve on the sources generated by occ (creates labels problems after)
        bad_ents  += [(1,14)] #extra curve added on surface of source
        for dt in bad_ents : 
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
    
    
    
    #### Renaming (usefull for several sources)
    
    if rename :
        mshmed=meshio.read(out) #load with meshio
        
        dt_rename = volsrcdts+surfsrcdts #dim tags of entities to rename
        ## Rename  volume elements
        for d,t in dt_rename :        
            if d == 3 :
                newlab = path.REFINT #interior elts with ref REFINT
            elif d == 2 :
                newlab = path.REFISO #surface elts with REFISIO
            else :
                print("wriong dim",d,"no renaming")
            maskcells = mshmed.cell_data["medit:ref"][d-1]==t #get tetra cells in t 
            ptslab = mshmed.cells[d-1].data[maskcells] #points labels from tetra cells in t 
            ptslab = np.unique(ptslab.flatten()) # remvoe the subarrray structure and points mentionned severaltimes
           
            # rename filtered points
            mshmed.point_data["medit:ref"][ptslab] = newlab
            mshmed.cell_data["medit:ref"][d-1][maskcells] = newlab
            
        mshmed.write(out) # save
        print("Elements renaming done")
        
    
    #### MMG Remeshing
    
    if mmg :

        # rename temporaly the mesh for the remeshing
        tmpf = out.replace(".mesh",".tmp.mesh")
        os.rename(out, tmpf)
        
        # Call to mmg3d for remeshing the background mesh
        log = open(path.LOGFILE,'a')

        # !!! no -nr option to detect the ridges and keep them for the future
        proc = subprocess.Popen([f"{path.MMG3D} -in {tmpf} -hmin {path.HMIN} -hmax {path.HMAX} -hausd {path.HAUSD} -hgrad {path.HGRAD} -optim -out {tmpf} -rmc"],shell=True,stdout=log)

        proc.wait()
        log.close()
        
        if ( proc.returncode != 0 ) :
            raise Exception(f"MMG remeshing failed, code {proc.returncode}")
        else :
            os.rename(tmpf,out) #rename to the correct name
            # print(os.listdir("./res/"))
            print("mmg remeshing done")



    




#### Tests
if  __name__ == "__main__":    
    build_mesh("./res/test.mesh",inhom=1,debug=1)
    
