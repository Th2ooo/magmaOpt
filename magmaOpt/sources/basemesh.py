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
    verbosity=4 => normal gmsh verbosity
    !! out must be a .mesh file for compatibility with freefem and mmg3d"""
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
    
    occ.synchronize()
    print(mod.getEntities())
    cube_faces_tags = [dt[1] for dt in mod.getEntities(2)]
    # print(cube_faces_tags)

    occ.addSphere(xs, ys, zs, 1,tag=2)
    
    occ.synchronize()
    print(mod.getEntities())
    
    
    sphere_tags = [dt[1] for dt in mod.getEntities(2) if dt[1] not in cube_faces_tags]
    print("a",sphere_tags)
    
    # gmsh.model.addPhysicalGroup(2, cube_faces_tags, 10)
    # gmsh.model.setPhysicalName(2, 10, "CubeBoundary")

    # gmsh.model.addPhysicalGroup(2, sphere_tags, 20)
    # gmsh.model.setPhysicalName(2, 20, "SphereInterface")
    
    # print("ent",mod.getEntitiesForPhysicalGroup(2, 10))

    
    occ.dilate([(3,2)],xs,ys,zs,rx,ry,rz)
    occ.cut([(3,1)],[(3,2)], removeTool=False) #cut the domain but keep interior of ellipse
    print(mod.getEntities())

    ###  !!! for testing charles code
    # occ.translate([(3,1),(3,2)],0.5,0.5,1.)
    
    occ.remove([(1,15)],True)

    
    
    occ.synchronize()
    # print("ent",mod.getEntitiesForPhysicalGroup(2, 10))

    # gmsh.fltk.run()

    #retag with the correct labels according to sotuto
    print(mod.getEntities())
    
    mod.setTag(2,12,path.REFDIR) #bottom surface = dirichlet boundary (blocked)
    mod.setTag(2,10,path.REFUP) #top surface = surface for error calculation

    mod.setTag(2,7,path.REFISO) #source surface = neumann surface = iso surface (loaded)



    # print("bound", mod.getBoundary([(2,path.REFISO)]))
    # source_bnd = mod.getBoundary([(2,path.REFISO)])
    # occ.synchronize()
    # occ.remove(source_bnd,True)
    # occ.synchronize()


    mod.setTag(3,1,101) #interior of the domain = Tint
    mod.setTag(3,2,102) #interior of the source = Text
    mod.setTag(3,101,path.REFEXT) #interior of the domain = Text
    mod.setTag(3,102,path.REFINT) #interior of the source = Tint
    

    print("FINAL",mod.getEntities())
    
    # gmsh.fltk.run()

    
    
    
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
        
    
    # print("trr",req_tri)

    
    if vizu : #launch gmsh UI
        gmsh.fltk.run()
        
        
    ####Saving
    
    # Check if we can write to this location
    if os.access(os.path.dirname(out), os.W_OK):
        print(f'Writing mesh in {out}')
        gmsh.write(out)
    else:
        print("No write permission in this directory!")

    
    
    
    
    # Close gmsh
    gmsh.finalize()
    
    if 0 :   # Add required entities at the end of the mesh file
        req_tri = gmsh.model.mesh.getElements(2, path.REFUP)[1][0] #required triangles tags

        print("Adding required faces")
        with open(out, 'r') as f:
            lines = f.readlines()
    
        # Find the end of the Tetrahedra section and insert RequiredTriangles
        new_lines = []
        for line in lines:
            new_lines.append(line)
            # Look for the line that marks the end of the Tetrahedra section
            if line.strip() == "End":
                # Add the RequiredTriangles section
                new_lines.append("\n")
                new_lines.append(f"RequiredTriangles\n")
                new_lines.append(f"{len(req_tri)}\n")
    
                for tri in req_tri:
                    # Write the three node numbers for each required triangle
                    new_lines.append(f"{tri}\n")
                new_lines.append("\nEnd\n")
                break
                
        # Write the modified content back to the file
        with open(out, 'w') as f:
            f.writelines(new_lines)
        print("Required faces added")
    

    
    
    
def inimsh(mesh,vizu=False,basic=True,verb=3) :
  
    
    build_mesh(mesh,vizu,basic,verb)
    print("GMSH meshing done")


    # rename temporaly the mesh for the remeshing
    tmpf = mesh.replace(".mesh",".tmp.mesh")
    os.rename(mesh, tmpf)
    
    # Call to mmg3d for remeshing the background mesh
    log = open(path.LOGFILE,'a')

    # !!! no -nr option to detect the ridges and keep them for the future
    proc = subprocess.Popen([f"{path.MMG3D} -in {tmpf} -hmin {path.HMIN} -hmax {path.HMAX} -hausd {path.HAUSD} -hgrad {path.HGRAD} -out {tmpf} -rmc"],shell=True,stdout=log)

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
    
    # build_mesh("./res/test.mesh",1)
    inimsh("./res/test.mesh",1)
