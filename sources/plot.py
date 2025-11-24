#!/usr/bin/pythonw
# -*-coding:Utf-8 -*

import sources.path as path
import sources.insar as insar
import numpy as np
import meshio
import os 
import pyvista as pv
from sources.utils import LOS_set,mesh_labmask


import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import colormaps as cm

SMALL_SIZE, MEDIUM_SIZE, BIGGER_SIZE = 18, 18, 30;
plt.rcParams.update({
    'font.family' : 'sans-serif' , 'font.size': MEDIUM_SIZE ,  'axes.titlesize' : MEDIUM_SIZE , 'axes.labelsize' : MEDIUM_SIZE + 2, 
    'xtick.labelsize' : MEDIUM_SIZE , 'ytick.labelsize' : MEDIUM_SIZE, 'legend.fontsize' : SMALL_SIZE + 1 , 'figure.max_open_warning' : 0,
    'figure.figsize' : (20, 10)
});


print("**********************************************")
print("**********       Plot evolution      *********")
print("**********************************************")
    
    
histo = np.genfromtxt(path.HISTO,delimiter=" ")
itl = histo[:,0].astype(int) #iterations
nit = itl[-1]#number of iteration
errl = histo[:,1] #errors
voll = histo[:,2] #volumes
col = histo[:,3] #
bxl = np.array(histo[:,4])
byl = np.array(histo[:,5])
bzl = np.array(histo[:,6])

bestit=np.argmin(errl)
lastit = int(itl[-1])



def plot_conv_mult(save=False) :
    """
    Multiviews plot of the  convergence of shape optimization procedure
    
    Parameters
    ----------
    save : TYPE, optional
        Save the plot in path.PLOTS folder. The default is False.

    Returns
    -------
    None.

    """
    ## Convergence plots
    
    # Load histogram
    bestit = np.argmin(errl)
    
    #Set integer ticker for the x axis
    fig, axs = plt.subplots(2,3,figsize=(40,20),constrained_layout=True)
    axs = axs.flatten()
    
    axs[0].set_title("Evolution of error",fontsize=10)
    axs[0].set_xlabel("iterations")
    axs[0].set_ylabel("Error")
    
    axs[0].semilogy(itl,errl)
    axs[0].grid()
    
    ax2=axs[0].twinx()
    ax2.set_ylabel("Coeff")
    ax2.plot(itl,col,color="tab:orange")
    axs[0].grid()
    axs[0].legend()
    
    
    axs[1].set_title("Evolution of volume ($m^3$)",fontsize=10)
    axs[1].set_xlabel("iterations")
    axs[1].set_ylabel("Volume")
    axs[1].plot(itl,voll,label="V")
    axs[1].legend()


    if path.ERRMOD in [0,1] :
        axs[1].hlines(4/3*np.pi*np.prod(path.RTs[0]),0,nit,linestyles="dashed",label="V obj")
    
        axs[2].plot(itl,np.sum((np.column_stack([bxl,byl,bzl])-path.XTs[0][np.newaxis,:])**2,axis=1)**0.5)
        axs[2].set_title("Evolution of distance",fontsize=10)
        axs[2].set_xlabel("iterations")
        axs[2].set_ylabel("Distance to objective (m)")
    
    
    axs[3].set_title("Evolution of barycenter position",fontsize=10)
    axs[3].set_xlabel("iterations")
    axs[3].set_ylabel("Position (m)")
    axs[3].plot(itl,bxl,label="$X_b$",color="red")
    if path.ERRMOD == 0 :
        axs[3].hlines(0,0,nit,linestyles="dashed",label="Xobj",colors="red")
    axs[3].legend()
    
    
    axs[4].set_title("Evolution of barycenter position",fontsize=10)
    axs[4].set_xlabel("iterations")
    axs[4].set_ylabel("Position (m)")
    axs[4].plot(itl,byl,label="$Y_b$",color="blue")
    if path.ERRMOD == 0 :
        axs[4].hlines(0,0,nit,linestyles="dashed",label="Yobj",colors="blue")
    axs[4].legend()
    
    axs[5].set_title("Evolution of barycenter position",fontsize=10)
    axs[5].set_xlabel("iterations")
    axs[5].set_ylabel("Position (m)")
    axs[5].plot(itl,bzl,label="$Z_b$",color="green")
    if path.ERRMOD == 0 :
        axs[5].hlines(-path.DEPTH,0,nit,linestyles="dashed",label="Zobj",colors="green")
    axs[5].legend()
        

    fig.tight_layout()
    fig.suptitle(f"Convergence plots, min error found {errl[bestit]} found at iteration {bestit} ")
    
    if save :
        plt.savefig(path.PLOTS+"plot_conv_mult.pdf")
    else :
        plt.show()

        
        

def plot_dmr(it=nit-2,ntplot=[],save=True) :
    """
    Plot data model residuals

    Parameters
    ----------
    it : TYPE, optional
        DESCRIPTION. The default is bestit.
    ntplot : TYPE, optional
        DESCRIPTION. The default is None.
    save : TYPE, optional
        DESCRIPTION. The default is True.

    """
    
    if path.ERRMOD != 2 : #LOS ERROR PLOT 
        print("Not implemented for this ERRMOD = ",path.ERRMOD)
        return None    

    if not ntplot :
        ntplot = list(range(path.NTCK))
        
    #create fig,axs
    fig,axs = plt.subplots(len(ntplot),3,figsize=(16,4*len(ntplot)),layout="constrained")
    fig.suptitle(f"Iteration {it}")

    if len(ntplot) == 1 : axs = axs[np.newaxis,:]
    
    # load mesh of interest on upper surface
    msh=meshio.read(path.step(it,"mesh"))
    mkup = mesh_labmask(msh,path.REFUP)
    locpl = msh.points[mkup]
    locpl[:,0:2] += path.ORMOD #readjust the plots to local coordinates
    
    #modeled disp
    modu = np.genfromtxt(path.step(it,"u.sol"),skip_header=8,skip_footer=1)[mkup]
    
    #get Insar data
    outtmp = path.PLOTS+"tmplos/"
    os.makedirs(outtmp,exist_ok=True)
 
    subi = -1
    for i,(tck,hea,inc) in enumerate(zip(path.TCKS,path.HEAS,path.INCS)) :
        print("Ploting",tck,"on",path.step(it,"mesh"))

        if i not in ntplot : continue
        else : subi+= 1; i=subi
        
        # data to plot
        losf = LOS_set(hea,inc)
        modlos = losf(modu[:,0],modu[:,1],modu[:,2])
        dat=insar.los2sol(tck, path.step(it,"mesh"), path.ORMOD)[:,2]
        k = insar.los2k(tck, path.step(it,"mesh"), path.ORMOD)[:,2]
                
        #mask where no data given
        loc = locpl[k==1]*1e-3
        modlos = modlos[k==1]*1e3
        dat = dat[k==1]*1e3
        
        # extrema values
        vmin = np.min(np.vstack((dat,modlos)))
        vmax = np.max(np.vstack((dat,modlos)))            

        # Plot data
        ax = axs[i,0]
        cm0=ax.scatter(loc[:,0],loc[:,1],c=dat,marker=".",cmap="jet",vmin=vmin,vmax=vmax)
        ax.set_aspect('equal', adjustable='box')
        scale = path.XEXT*1e-3/20
        ax.arrow(ax.get_xbound()[0] + 4*scale, ax.get_ybound()[1] - 5*scale,
                 scale*3*np.sin(hea), scale*3*np.cos(hea), 
                 color="black", lw=3,  # Thinner line (was lw=5)
                 head_width=0.6*scale, head_length=1*scale,  # Bigger head
                 length_includes_head=True)
        ax.arrow(ax.get_xbound()[0] + 4*scale, ax.get_ybound()[1] - 5*scale,
                 (scale*2)*np.sin(hea+np.pi/2), (scale*2)*np.cos(hea+np.pi/2),
                 color="black", lw=3,  # Thinner line (was lw=5)
                 head_width=0.6*scale, head_length=1*scale,  # Bigger head
                 length_includes_head=True) 
        ax.ticklabel_format(style='sci',scilimits=(0,0), useMathText=True)
        if not ntplot :
            ax.set_title(f"Data track {tck}")
        else : 
            ax.set_title("Data")
            
            
        fig.colorbar(cm0,label="LOS displacements (mm)", ax=ax, location="left")

        #plot model
        ax = axs[i,1]
        ax.scatter(loc[:,0],loc[:,1],c=modlos,marker=".",cmap="jet",vmin=vmin,vmax=vmax)
        ax.set_aspect('equal', adjustable='box')
        ax.ticklabel_format(style='sci',scilimits=(0,0), useMathText=True)
        ax.set_title("Model")

        # divider = make_axes_locatable(ax)
        # cax = divider.append_axes("right", size="5%", pad=0.2)
        
        #plot residuals
        resi = dat-modlos
        extr = np.max(np.abs(resi))
        ax = axs[i,2]
        cm2=ax.scatter(loc[:,0],loc[:,1],c=resi,marker=".",cmap="coolwarm",vmin=-extr,vmax=extr)
        ax.set_aspect('equal', adjustable='box')
        ax.set_title("Residuals")
        ax.ticklabel_format(style='sci',scilimits=(0,0), useMathText=True)
        fig.colorbar(cm2,label="LOS residuals (mm)", ax=ax, location='right')


        
        
    for i in range(len(ntplot)) :
        axs[i,0].set(ylabel="Northing (km)") 
    for i in range(3) :
        axs[-1,i].set(xlabel="Easting (km)") 


  
    if save :
        plt.savefig(path.PLOTS+"DMRplot.pdf")
        plt.savefig(path.PLOTS+"DMRplot.png")

    else :
        plt.show()
            
    



def plot_conv_mono(nit=lastit,save=False) :
    ## Convergence plots    
    fig, ax = plt.subplots(figsize=(15,10))

    ax1 = ax.twinx()
    axcol = cm.set1[0].colors
    p1=ax1.plot(itl[:nit],col[:nit],color=axcol,linewidth=1,label="Step size $\\tau$",zorder=1)
    ax1.spines['right'].set_visible(False)  # Hide right spine
    ax1.spines['left'].set_position(('outward', 0))  # Share left spine
    ax1.tick_params(axis='y',direction="in", pad=-40,colors=axcol)
    ax1.yaxis.set_label_position('left')
    ax1.set_ylabel("Step size $\\tau$",color=axcol,labelpad=-60)
    ax1.yaxis.tick_left()
    ax1.set_axisbelow(True)
    # ax1.set_zorder(ax.get_zorder() - 1)  # Force ax2 behind ax1

    
    ax2 = ax.twinx()
    axcol = cm.vivid[0].colors
    if path.ERRMOD != 2:
        volobj = 4/3*np.pi*np.prod(path.RTs[0]) #volume of objective shape
        voln = voll/volobj
        ax2.set_ylabel("Volume ratio $V_{\Omega}/V_{obj}$",color=axcol,labelpad=-70)
    else :
        voln = voll
        ax2.set_ylabel("Volume $V_{\Omega}\quad (m^3)$",color=axcol,labelpad=-70)
        
    p2=ax2.plot(itl[:nit],voln[:nit],color=axcol,linewidth=1,zorder=1)
    
    ax2.spines['left'].set_visible(False)  # Hide right spine
    ax2.spines['right'].set_position(('outward', 0))  # Share left spine
    ax2.tick_params(axis='y',direction="in", pad=-40, colors=axcol)
    ax2.yaxis.set_label_position('right')


    
    axcol = cm.vivid[2].colors
    if path.ERRMOD != 2 :
        ax3 = ax.twinx()
        distn = np.sum((np.column_stack([bxl,byl,bzl])-path.XTs[0][np.newaxis,:])**2,axis=1)**0.5
        ax3.set_ylabel("Shapes distance $||\mathbf{b}_{\Omega}-\mathbf{b}_{obj}||$ ($m$)",color=axcol,labelpad=20)
    
        p3=ax3.plot(itl[:nit],distn[:nit],color=axcol,linewidth=1,ls="--",label="Distance of shapes $||\mathbf{x}_{\Omega}-x_{obj}||$",zorder=1)
        ax3.tick_params(axis='y',colors=axcol)
        ax3.zorder = 1 
        ax3.patch.set_visible(False)
        ax3.margins(x=0.1)

    
    
    axcol ="blue"
    p=ax.semilogy(itl[:nit],errl[:nit],color=axcol,linewidth=3, zorder=5, label="Error $J_{LS}$")
    ax.tick_params(axis='y',colors=axcol)
    ax.set_ylabel("Error $J_{LS}\quad (m^4)$",color=axcol,labelpad=5)
    ax.set_xlabel("Iterations")
    ax.xaxis.set_label_position('top')
    ax.xaxis.set_major_locator(ticker.FixedLocator(np.arange(0,nit,nit//10)))
    ax.tick_params(axis="x", bottom=True, top=True, labelbottom=True, labeltop=True)

                    

    ax.grid(alpha=0.4)
    ax.patch.set_visible(False)
    ax1.patch.set_visible(False)
    ax2.patch.set_visible(False)
    
    ax1.zorder = 3
    ax2.zorder = 2
    ax.zorder = 4
    
    ax.margins(x=0.1)
    ax1.margins(x=0.1)
    ax2.margins(x=0.1)
        

    if save :
        plt.savefig(path.PLOTS+"plot_conv_mono.pdf")
        plt.savefig(path.PLOTS+"plot_conv_mono.png")

    else :
        plt.show()
        
        
        




def plot_shape(it=nit-2,save=False) :
    """Show multiple views of the current shape"""
    # Create a plotter with 4 subplots (2x2 grid)
    plo = pv.Plotter(shape=(2, 2), title="Multi-view optimization animation", window_size=[1200,1200])    
    
    
    # Create objects
    if path.ERRMOD != 2 :
        sph_T = []
        for rs,xs in zip(path.RTs,path.XTs) :
            sph_T += [pv.ParametricEllipsoid(rs[0],rs[1],rs[2])]  #sphere at the objective source loc
            sph_T[-1].translate(xs,inplace=True)
            
    dom_box = pv.Box(bounds=(-path.XEXT/2, path.XEXT/2, -path.YEXT/2, path.YEXT/2, -path.ZEXT, 0.0))

                    
    # Set up each subplot
    for i in range(2):
        for j in range(2) :
            plo.subplot(i,j)
            plo.add_axes(interactive=False, line_width=4)
            
            if  path.ERRMOD != 2 :
                for sph in sph_T :
                    plo.add_mesh(sph, style="surface", color="blue", opacity=0.3)
                    
            # Add domain box to all views
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
            plo.add_mesh(mshpv, color="orangered", opacity=1)
            # Add grid to help visualization
            plo.show_grid(xtitle="X", ytitle="Y", ztitle="Z", 
                grid=True,
                location='outer',
                font_size=10,
                color='gray',
                fmt="%.0f")
            c+= 1
            
    plo.subplot(0,0)# Add iteration and error info to the firset subplot
    plo.add_text(f"it {it}", "lower_right", color='black')

    if save :
        plo.save_graphic(path.PLOTS+"shape.pdf", f"Shape at it {it}")
        plo.save_graphic(path.PLOTS+"shape.svg", f"Shape at it {it}")

    plo.show()

 




print("**********************************************")
print("**************    End of Plot   **************")
print("**********************************************")


#### Tests
if __name__ == "__main__" :
    print(f"CURRENT IT {nit-1}, BESTIT {bestit}")
    plot_shape(it=bestit,save=1)
    plot_dmr(it=bestit,save=1)
    plot_dmr(it=nit-1,save=0)
    plot_conv_mult(save=1)
    plot_conv_mono(nit-1,save=1)
    print(f"CURRENT IT {nit-1}, BESTIT {bestit}")


        
