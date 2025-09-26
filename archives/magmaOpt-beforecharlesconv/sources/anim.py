#!/usr/bin/pythonw
# -*-coding:Utf-8 -*
#TO Run from spyder
import os

import subprocess

import sys
import sources.path as path
import numpy as np
import pyvista as pv
import meshio

content = np.genfromtxt(path.HISTO,delimiter=" ")
nit = content.shape[0] #number of iteration
itl = content[:,0] #iterations
El = content[:,1] #errors



def gen_anim() :
    print("**********************************************")
    print("**********     Source  animation  *********")
    print("**********************************************")
    #TODO : add 2d x,y,z  views  
    plo = pv.Plotter(title="Tset") #,off_screen=False,notebook=False)
    plo.open_movie(path.RES+"shape.mp4")
    
    #test
    # plo = pv.Plotter(off_screen=True)
    if 1 :
        plo.add_axes(interactive=False,line_width=4)
        ##add McTigue sol ref
        sph_vrai = pv.Sphere(radius=path.RVRAI,center=(0.0,0.0,-path.DEPTH))
        plo.add_mesh(sph_vrai,style="surface",color="blue",opacity=0.3)
        ## add dmoamin box
        dom_box = pv.Box(bounds=(-path.XEXT/2,path.XEXT/2,-path.YEXT/2,path.YEXT/2,-path.ZEXT,0.0))
        plo.add_mesh(dom_box,style='wireframe',color="black")
        
    if 0 :
        # ADD REFERENCE SOL FROM CHARLES (in case processing Charle's  code)
        dom_box = pv.Box(bounds=(0,1,0,1,0,1)) 
        plo.add_mesh(dom_box,style='wireframe',color="black")
        mshfile = "/media/th2o/GrosSSD/Cours/magmaOpt_dev/code_charles/meshT3.mesh"
        msh=meshio.read(mshfile)
        mk = msh.cell_data["medit:ref"][1]== path.REFISO #criterion with label
        faces = msh.cells[1].data[mk]
        nbs = np.full((faces.shape[0],1),3)
        faces = np.hstack((nbs,faces))
        faces = np.ravel(faces)
        mshpv = pv.PolyData(msh.points,faces)
        po = plo.add_mesh(mshpv, color="blue",  opacity =0.2) 
    
    for it in range(nit-3) :
        # if it > 10 : break1
        print(f"it no {it}")
        mshfile = path.step(it,"mesh")  
        msh=meshio.read(mshfile)
        
        #creating the face array for pyvista
        mk = msh.cell_data["medit:ref"][1]== path.REFISO #criterion with label
        faces = msh.cells[1].data[mk]
        nbs = np.full((faces.shape[0],1),3)
        faces = np.hstack((nbs,faces))
        faces = np.ravel(faces)
        mshpv = pv.PolyData(msh.points,faces)
        mspl = plo.add_mesh(mshpv, color="orangered",  opacity =1) 
        
    
        txt = plo.add_text(f"it {it}","lower_right",color='black')
        
        err = El[it]
        txt2 = plo.add_text(f"Error {err:.3E}","upper_left",color='black')
        
        # break
    
        plo.write_frame()
        
        
        plo.remove_actor([mspl,txt,txt2])

    # plo.show()

    plo.close()
    
    
    # pygifsicle.optimize(path.RES+"shape.gif") # to compress the GIF1



gen_anim()

print("**********************************************")
print("**************    End of Plot   **************")
print("**********************************************")
