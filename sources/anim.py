#!/usr/bin/pythonw
# -*-coding:Utf-8 -*
#TO Run from spyder
import os

import subprocess
from pathlib import Path
import sources.path as path
import numpy as np
import pyvista as pv
import meshio


import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import rcParams
import matplotlib.image as mpimg



content = np.genfromtxt(path.HISTO,delimiter=" ")
nit = content.shape[0] #number of iteration
itl = content[:,0] #iterations
El = content[:,1] #errors
col = content[:,3] #


print("**********************************************")
print("**********     Source  animation     *********")
print("**********************************************")

def anim_simple() :

    #TODO : add 2d x,y,z  views  
    plo = pv.Plotter(title="Tset") #,off_screen=False,notebook=False)
    plo.open_movie(path.PLOTS+"shape_simple.mp4")
    
    #test
    # plo = pv.Plotter(off_screen=True)
    if 1 :
        plo.add_axes(interactive=False,line_width=4)
        ##add McTigue sol ref
        sph_vrai = pv.Sphere(radius=path.RVRAI,center=(path.XST,path.YST,-path.DEPTH))
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
    
    
    
    
    
    
def anim_multiview() :
    """!!!!! Very slow"""
    # Create a plotter with 4 subplots (2x2 grid)
    plo = pv.Plotter(shape=(2, 2), title="Multi-view optimization animation", window_size=[1200,1200])
    plo.open_movie(path.PLOTS+"shape_multview.mp4")
    
    
    # Set up each subplot
    for i in range(2):
        for j in range(2) :
            print(i,j)
            plo.subplot(i,j)
            plo.add_axes(interactive=False, line_width=4)
            
            # Add reference sphere to all views
            sph_vrai = pv.Sphere(radius=path.RVRAI, center=(path.XST, path.YST, -path.DEPTH))
            plo.add_mesh(sph_vrai, style="surface", color="blue", opacity=0.3)
            
            # Add domain box to all views
            dom_box = pv.Box(bounds=(-path.XEXT/2, path.XEXT/2, -path.YEXT/2, path.YEXT/2, -path.ZEXT, 0.0))
            plo.add_mesh(dom_box, style='wireframe', color="black")
    
    # Set specific camera angles for each subplot
    plo.subplot(0,0)
    plo.camera_position = "iso"
    
    plo.add_text("3D View", "upper_left", color='black')
    
    plo.subplot(0,1)
    plo.camera_position = "xy"
    plo.add_text("Top View (XY)", "upper_left", color='black')
    
    plo.subplot(1,0)
    plo.camera_position = "xz"
    plo.add_text("Front View (XZ)", "upper_left", color='black')
    
    plo.subplot(1,1)
    plo.camera_position = "yz"
    plo.add_text("Side View (YZ)", "upper_left", color='black')
    
    # Store mesh actors for each subplot so we can remove them later
    mesh_actors = [[] for _ in range(4)]
    
    plo.write_frame()
    
    
    for it in range(nit-3):
        print(f"it no {it}")
        mshfile = path.step(it, "mesh")  
        msh = meshio.read(mshfile)
        
        # Creating the face array for pyvista
        mk = msh.cell_data["medit:ref"][1] == path.REFISO
        faces = msh.cells[1].data[mk]
        nbs = np.full((faces.shape[0], 1), 3)
        faces = np.hstack((nbs, faces))
        faces = np.ravel(faces)
        mshpv = pv.PolyData(msh.points, faces)
        
        
        c = 0
        # Add mesh to all subplots
        for i in range(2):
            for j in range(2) :
                plo.subplot(i,j)
                mesh_actor = plo.add_mesh(mshpv, color="orangered", opacity=1)
                mesh_actors[c].append(mesh_actor)
                # Add grid to help visualization
                plo.show_grid(xtitle="X", ytitle="Y", ztitle="Z", 
                    grid=True,
                    location='outer',
                    font_size=10,
                    color='gray',
                    fmt="%.0f")
                c+= 1
                
        plo.subplot(0,0)# Add iteration and error info to the firset subplot
        text1 = plo.add_text(f"it {it}", "lower_right", color='black')
        text2 = plo.add_text(f"Error {El[it]:.3E}", "upper_right", color='black')
        text_actors =[text1, text2]
        
        plo.write_frame()
        # plo.show()
        # Remove mesh and text from all subplots for next frame
        
        c = 0
        for actor in text_actors:
            plo.remove_actor(actor)
        for i in range(2):
            for j in range(2) :
                plo.subplot(i,j)
                for actor in mesh_actors[c]:
                    plo.remove_actor(actor) 
                c += 1
    
    plo.close()




def export_3Dviews(nit=nit):
    """Export 3D and side view images for each iteration without displaying windows
    MODIFY to add N views"""
    print("**********************************************")
    print("*****  Headless Image Export for Animation *****")
    print("**********************************************")
    
    # Create output directories
    os.makedirs(path.PLOTS + "3d_views/", exist_ok=True)
    os.makedirs(path.PLOTS + "side_views/", exist_ok=True)
   
    for it in range(nit):
        
        f3D = Path(path.PLOTS + f"3d_views/frame_{it:04d}.png")
        fsi = Path(path.PLOTS + f"side_views/frame_{it:04d}.png")
        
        if f3D.is_file() and fsi.is_file() :
            print(f"View it {it} already exist, skipped")
            continue
        
        print(f"Exporting iteration {it}")
        mshfile = path.step(it, "mesh")  
        
        # Create mesh source for PyVista
        msh = meshio.read(mshfile)
        mk = msh.cell_data["medit:ref"][1] == path.REFISO
        faces = msh.cells[1].data[mk]
        nbs = np.full((faces.shape[0], 1), 3)
        faces = np.hstack((nbs, faces))
        faces = np.ravel(faces)
        mshpv = pv.PolyData(msh.points, faces)
        # Create other objeccts
        sph_T = []
        if  path.ERRMOD != 2 :
            for rs,xs in zip(path.RTs,path.XTs) :
                sph_T += [pv.ParametricEllipsoid(rs[0],rs[1],rs[2])]  #sphere at the objective source loc
                sph_T[-1].translate(xs,inplace=True)
        dom_box = pv.Box(bounds=(-path.XEXT/2, path.XEXT/2, -path.YEXT/2, path.YEXT/2, -path.ZEXT, 0.0))

        if not f3D.is_file() :
            # Export 3D view
            plo_3d = pv.Plotter(off_screen=True, window_size=[800, 800])
            plo_3d.add_axes(interactive=False, line_width=4)
            
            # Add reference objects
            if  path.ERRMOD != 2 :
                for sph in sph_T :
                    plo_3d.add_mesh(sph, style="surface", color="blue", opacity=0.3)
            plo_3d.add_mesh(dom_box, style='wireframe', color="black")
            
            # Add main mesh and set camera
            plo_3d.add_mesh(mshpv, color="orangered", opacity=1)
            plo_3d.camera_position ="iso"
            plo_3d.show_grid(xtitle="X", ytitle="Y", ztitle="Z", color='gray')
            plo_3d.add_text(f"Iteration {it}\nError: {El[it]:.3E}", position="upper_left", color='black', font_size=12)
    
            # Save 3D view
            plo_3d.screenshot(f3D)
            plo_3d.close()
        
        if not fsi.is_file() :
            # Export side view
            plo_side = pv.Plotter(off_screen=True, window_size=[800, 800])
            plo_side.add_axes(interactive=False, line_width=4)
            
            # Add reference objects (optional - can skip for side view)
            if  path.ERRMOD != 2 :
                for sph in sph_T :
                    plo_side.add_mesh(sph, style="surface", color="blue", opacity=0.3)
            plo_side.add_mesh(dom_box, style='wireframe', color="black")
            
            # Add main mesh and set side camera
            plo_side.add_mesh(mshpv, color="orangered", opacity=1)
            plo_side.camera_position = "xy"
            plo_side.show_grid(xtitle="X", ytitle="Y", ztitle="Z",  color='gray')
    
            
            # Save side view
            plo_side.screenshot(fsi)
            plo_side.close()
    
    print("Image export completed!")
    
    

def composite_animation(nit=nit-3,fps=5) :
    """Create a composite animation with error curve and PyVista views
    times= approximate time in seconds of the movie
    
    !!!! Requires imageio_ffmpeg to be installed from PIP"""
    
    import imageio_ffmpeg
    rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()

    
    print("Creating composite animation...")
    
    # First executeexport pyvista animations if not the case
    export_3Dviews(nit)
        
    # Create figure with 3 subplots
    fig = plt.figure(figsize=(20, 15),layout='constrained')
    axs = fig.subplot_mosaic( "AB\nAC")
    fig.suptitle('Shape Optimization Progress', fontsize=16)
    
    # Subplot 1: Error curve
    ax1 = axs['B']
    p1,=  ax1.plot(itl, El, 'b-', linewidth=3, label='Error')
    ax1.set_xlabel('Iteration')
    ax1.set_ylabel('Error')
    ax1.set_yscale('log')  # Use log scale if errors vary widely
    ax1.grid(True, alpha=0.3)
    
    ax11=ax1.twinx()
    ax11.set_ylabel("Step size")
    p11, =ax11.plot(itl,col,color="tab:red",label="Step size")
    
    
    # Vertical line for current iteration (will be updated)
    vline = ax1.axvline(x=0, color='darkorange', linestyle='--', linewidth=2,label="Current iteration")
    iteration_text = ax1.text(0.02, 0.98, '', transform=ax1.transAxes, verticalalignment='top')
    
    ax1.legend(handles=[p1, p11,vline])


    ax2 = axs['A']
    ax3 = axs['C']
    
    
    # Initialize image boxes
    it=0
    img = mpimg.imread(path.PLOTS + f"3d_views/frame_{it:04d}.png")
    img_3d = ax2.imshow(img)
    img = mpimg.imread(path.PLOTS + f"side_views/frame_{it:04d}.png")
    img_side = ax3.imshow(img)
    
    ax2.set_title('3D View')
    ax3.set_title('Top View')
    ax2.axis('off')
    ax3.axis('off')
    
    # plt.show(block=True)
    
    def update_frame(it):
        """Update function for each animation frame"""
        print(f"Processing frame {it}")
        
        # Update error plot
        vline.set_xdata([itl[it], itl[it]])
        iteration_text.set_text(f'Iteration: {itl[it]:.0f}\nError: {El[it]:.3E}')
        
        # Load and update 3D view image
        try:
            img = mpimg.imread(path.PLOTS + f"3d_views/frame_{it:04d}.png")
            img_3d.set_data(img)
        except FileNotFoundError:
            print(f"3D image for iteration {it} not found")
        
        # Load and update side view image
        try:
            img = mpimg.imread(path.PLOTS + f"side_views/frame_{it:04d}.png")
            img_side.set_data(img)
        except FileNotFoundError:
            print(f"Side image for iteration {it} not found")
        
        return vline, iteration_text, img_3d, img_side
    
    # Create animation
    anim = animation.FuncAnimation(
        fig, update_frame, frames=range(nit), 
        interval=200, blit=False, repeat=True)
    

    
    # Save animation
    # fps = max(int(nit/times),1)
    print("FPS selected",fps)
    anim.save(filename= path.PLOTS+'animation.mp4', 
              writer='ffmpeg', fps=fps, dpi=150)
    
    plt.close()
    print("Composite animation saved!")


print("**********************************************")
print("**********    End of animation  **************")
print("**********************************************")



if __name__ == "__main__" :
    # export_3Dviews()
    composite_animation(nit=2500,fps=30)

