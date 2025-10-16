#!/usr/bin/pythonw
# -*-coding:Utf-8 -*

import sources.path as path
import sources.insar as insar
import numpy as np
import meshio
import os 
from utils import LOS_set


import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import mpltern #optional, used for ternary plot
SMALL_SIZE, MEDIUM_SIZE, BIGGER_SIZE = 18, 15, 30;
plt.rcParams.update({
    'font.family' : 'sans-serif' , 'font.size': MEDIUM_SIZE ,  'axes.titlesize' : MEDIUM_SIZE , 'axes.labelsize' : MEDIUM_SIZE + 2, 
    'xtick.labelsize' : MEDIUM_SIZE , 'ytick.labelsize' : MEDIUM_SIZE, 'legend.fontsize' : SMALL_SIZE + 1 , 'figure.max_open_warning' : 0,
    'figure.figsize' : (20, 10)
});


print("**********************************************")
print("**********       Plot evolution      *********")
print("**********************************************")
    
    
histo = np.genfromtxt(path.HISTO,delimiter=" ")
nit = histo.shape[0] #number of iteration
itl = histo[:,0] #iterations
errl = histo[:,1] #errors
voll = histo[:,2] #volumes
col = histo[:,3] #
bxl = np.array(histo[:,4])
byl = np.array(histo[:,5])
bzl = np.array(histo[:,6])

bestit=np.argmin(errl)

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

        
        

def plot_dmr(it=nit-2,ntplot=None,save=True) :
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

    Returns
    -------
    None.

    """
    
    if path.ERRMOD != 2 : #LOS ERROR PLOT 
        print("Not implemented for this ERRMOD = ",path.ERRMOD)
        return None    
        
    mono = False
    if isinstance(ntplot,int) :
        mono = True
    
        
    if not mono :
        fig,axs = plt.subplots(path.NTCK,3,figsize=(14,3.5*path.NTCK),layout="constrained")
    else :
        fig,axs = plt.subplots(1,3,figsize=(14,3.5),layout="constrained")
        axs = axs[np.newaxis,:]
    print(axs)
    msh=meshio.read(path.step(it,"mesh"))
    mkup = msh.point_data["medit:ref"]==path.REFUP
    loc = msh.points[mkup]
    
    #modeled disp
    modu = np.genfromtxt(path.step(it,"u.sol"),skip_header=8,skip_footer=1)[mkup]
    

    #get Insar data
    outtmp = path.PLOTS+"tmplos/"
    os.makedirs(outtmp,exist_ok=True)
 
    for i,(tck,hea,inc) in enumerate(zip(path.TCKS,path.HEAS,path.INCS)) :
        print("Ploting",tck)
        if mono :
            if i != ntplot : continue
            else : i=0
        
        #reinterpolate los on the choosen mesh
        solf = outtmp+f"losu_it{it}_{i}.sol"
        insar.los2sol(tck, path.step(it,"mesh"), solf,path.ORMOD)

        #plot data
        dat=np.genfromtxt(solf,skip_header=8)[mkup]
  
        vmin = np.min(dat)
        vmax = np.max(dat)            

        ax = axs[i,0]
        ax.scatter(loc[:,0],loc[:,1],c=dat,marker=".",cmap="jet",vmin=vmin,vmax=vmax)
        ax.set_aspect('equal', adjustable='box')
        scale = path.XEXT/20
        ax.arrow(ax.get_xbound()[0]+4*scale,ax.get_ybound()[1]-4*scale,
                 scale*2*np.sin(hea),scale*2*np.cos(hea),color="black",lw=5)
        ax.arrow(ax.get_xbound()[0]+4*scale,ax.get_ybound()[1]-4*scale,
                 (scale*0.9)*np.sin(hea+np.pi/2),(scale*0.9)*np.cos(hea+np.pi/2),color="black",lw=5)
        if not ntplot :
            ax.set_title(f"Data track {tck}")
        else : 
            ax.set_title("Data")
        
        #plot model
        ax = axs[i,1]
        losf = LOS_set(hea,inc)
        modlos = losf(modu[:,0],modu[:,1],modu[:,2])
        ax.scatter(loc[:,0],loc[:,1],c=modlos,marker=".",cmap="jet") #,vmin=vmin,vmax=vmax)
        ax.set_aspect('equal', adjustable='box')
        ax.set_title("Model")

        #plot residuals
        ax = axs[i,2]
        cm=ax.scatter(loc[:,0],loc[:,1],c=dat-modlos,marker=".",cmap="jet",vmin=vmin,vmax=vmax)
        ax.set_aspect('equal', adjustable='box')
        ax.set_title("Residuals")
        
        fig.colorbar(cm,label="LOS (mm)",location="right")
  
    if save :
        plt.savefig(path.PLOTS+"DMRplot.pdf")
    else :
        plt.show()
            
    



def plot_conv_mono(save=False) :
    ## Convergence plots    
    fig, ax = plt.subplots(figsize=(20,12))
    axcol = "blue"
    p=ax.semilogy(itl,errl,color=axcol,linewidth=2.5, zorder=5, label="Error $J_{LS}$")
    ax.tick_params(axis='y',colors=axcol)
    ax.set_ylabel("Error $J_{LS}$ ($m^4$)",color=axcol,labelpad=15)
    ax.set_xlabel("Iterations")
    ax.xaxis.set_label_position('top')
    ax.xaxis.set_major_locator(ticker.FixedLocator(np.arange(0,nit,nit//10)))
    ax.tick_params(axis="x", bottom=True, top=True, labelbottom=True, labeltop=True)

                    
    ax1 = ax.twinx()
    axcol = "red"
    p1=ax1.plot(itl,col,color=axcol,linewidth=1,label="Step size $\\tau$",zorder=3)
    ax1.spines['right'].set_visible(False)  # Hide right spine
    ax1.spines['left'].set_position(('outward', 0))  # Share left spine
    ax1.tick_params(axis='y',direction="in", pad=-30,colors=axcol)
    ax1.yaxis.set_label_position('left')
    ax1.set_ylabel("Step size $\\tau$",color=axcol,labelpad=-60)
    ax1.yaxis.tick_left()

    
    ax2 = ax.twinx()
    axcol = "forestgreen"
    if path.ERRMOD != 2:
        volobj = 4/3*np.pi*np.prod(path.RTs[0]) #volume of objective shape
        voln = voll/volobj
        ax2.set_ylabel("Volume ratio $V_{\Omega}/V_{obj}$",color=axcol,labelpad=20)
    else :
        voln = voll
        ax2.set_ylabel("Volume $V_{\Omega}$",color=axcol,labelpad=20)
        
    p2=ax2.plot(itl,voln,color=axcol,linewidth=1,ls="--",zorder=2)
    ax2.tick_params(axis='y',colors=axcol)


    
    ax3 = ax.twinx()
    axcol = "darkorange"
    if path.ERRMOD != 2 :
        distn = np.sum((np.column_stack([bxl,byl,bzl])-path.XTs[0][np.newaxis,:])**2,axis=1)**0.5
        ax3.set_ylabel("Shapes distance $||\mathbf{b}_{\Omega}-\mathbf{b}_{obj}||$ ($m$)",color=axcol,labelpad=-70)

    else :
        distn = np.sum((np.column_stack([bxl,byl,bzl])-np.array([0,0,-path.ZEXT/2])[np.newaxis,:])**2,axis=1)**0.5
        ax3.set_ylabel("Shape distance to center of the domain $||\mathbf{b}_{\Omega}-\mathbf{b}_{D}||$ ($m$)",color=axcol,labelpad=-70)


    
    
    p3=ax3.plot(itl,distn,color=axcol,linewidth=1,ls="--",label="Distance of shapes $||\mathbf{x}_{\Omega}-x_{obj}||$",zorder=1)
    
    ax3.spines['left'].set_visible(False)  # Hide right spine
    ax3.spines['right'].set_position(('outward', 0))  # Share left spine
    ax3.tick_params(axis='y',direction="in", pad=-40, colors=axcol)
    ax3.yaxis.set_label_position('right')
    
    
    ax.grid(alpha=0.5)
    


    

    # ax.legend(handles=p+p1+p2+p3, loc='lower left')

    if save :
        plt.savefig(path.PLOTS+"plot_conv_mono.pdf")
    else :
        plt.show()
        
        
#!!!! TERNARY DOES NOT WORK FOR INDEPENDANT VARIABLES
def plot_traj(save=False) :
    """
    Ternary plot to vizualize the trajectory of the barycenter as well as the volume change

    Returns
    -------
    None.

    """
    # Convert 3D coordinates to ternary coordinates (sum to 1)
    def to_ternary(x, y, z):
        bxlt,bylt,bzlt = x+path.XEXT/2,y+path.YEXT/2,z+path.ZEXT
        bxlt,bylt,bzlt = bxlt/path.XEXT,bylt/path.YEXT,bzlt/path.ZEXT
        return bxlt,bylt,bzlt
    
    fig = plt.figure(figsize=(10,10),layout="constrained")
    ax = fig.add_subplot(projection="ternary")
    
    # Convert data to ternary coordinates
    bxl_tern, byl_tern, bzl_tern = to_ternary(np.array(bxl), np.array(byl), np.array(bzl))
    
    ax.set_tlim(0.2, 0.8)    # X limits
    ax.set_llim(0.2, 0.8)    # Y limits  
    ax.set_rlim(0.2, 0.8)    # Z limits (focus on high Z)
    
    # Plot the converted data
    c = ax.scatter(bxl_tern, byl_tern, bzl_tern, c=itl, edgecolor="none", cmap="turbo",label="Succesive position of the shape")
    fig.colorbar(c, label="Iteration number")
    
    ax.set_tlabel("X (m)")
    ax.set_llabel("Y (m)") 
    ax.set_rlabel("Z (m)")
    
    if path.ERRMOD != 2 :
        xst_tern, yst_tern, zst_tern = to_ternary(
            np.array([path.XTs[0][0]]), 
            np.array([path.XTs[0][1]]), 
            np.array([path.XTs[0][2]])
        )
        ax.scatter(xst_tern, yst_tern, zst_tern, marker='x', c="red", s=100,label="Objective source position")
        
    ax.legend()

    
    if save :
        plt.savefig(path.PLOTS+"tern_traj.pdf")
    else :
        plt.show()


print("**********************************************")
print("**************    End of Plot   **************")
print("**********************************************")


if __name__ == "__main__" :
    plot_conv_mult(save=1)
    plot_conv_mono(1)
    plot_traj(1)
    plot_dmr(it=bestit,save=1)
    plot_dmr(save=0,)
    
    print(f"CURRENT IT {nit-2}, BESTIT {bestit}")

        
