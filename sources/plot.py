#!/usr/bin/pythonw
# -*-coding:Utf-8 -*
#TO Run from spyder
import os
# os.chdir("/home/th2o/Documents/Cours/magmaOpt_dev/magmaOpt")
os.chdir("/media/th2o/GrosSSD/Cours/magmaOpt_dev/magmaOpt")

import subprocess

import sys
import sources.path as path
import sources.insar as insar
import numpy as np
import matplotlib.pyplot as plt
import pyvista as pv
import meshio
from sources.utils import *
#from artist import *

content = np.genfromtxt(path.HISTO,delimiter=" ")
nit = content.shape[0] #number of iteration
itl = content[:,0] #iterations
El = content[:,1] #errors

voll = content[:,2] #volumes
col = content[:,3] #
bxl = np.array(content[:,4])
byl = np.array(content[:,5])
bzl = np.array(content[:,6])



def plot_conv(save=False) :
    ## Convergence plots
    print("**********************************************")
    print("**********       Plot histogram      *********")
    print("**********************************************")
    
    # Load histogram
    bestit = np.argmin(El)
    
    #Set integer ticker for the x axis
    fig, axs = plt.subplots(2,3,figsize=(40,20),constrained_layout=True)
    axs = axs.flatten()
    
    axs[0].set_title("Evolution of error",fontsize=10)
    axs[0].set_xlabel("iterations")
    axs[0].set_ylabel("Error")
    
    axs[0].plot(itl,El)
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
    if path.ERRMOD == 0 :
        axs[1].hlines(4/3*np.pi*path.RVRAI**3,0,nit,linestyles="dashed",label="V obj")
    axs[1].legend()
    
    if path.ERRMOD == 0 :
        axs[2].plot(itl,np.sqrt(bxl**2+byl**2+(bzl+path.DEPTH)**2))
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
    fig.suptitle(f"Convergence plots, min error found {El[bestit]} found at iteration {bestit} ")
    
    if save :
        plt.savefig(path.PLOTS+"convplot.png")
    else :
        plt.show()





def plot_dmr(it) :
    """Plot data model residuals"""
    
    print("**********************************************")
    print("**********     Data-model residuals  *********")
    print("**********************************************")
    
    domex = Extent()
    domex.init_with_range(path.XEXT,path.YEXT,path.ZEXT)
    art = Artist(2,3,extent=domex,fonts=10)
    # art.init_topo(100,path=svartDEM,ori=path.ORMOD)
    
    msh=meshio.read(path.step(it,"mesh"))
    mkup = msh.point_data["medit:ref"]==path.REFUP
    loc = msh.points[mkup]
    
    #modeled disp
    modu = np.genfromtxt(path.step(it,"u.sol"),skip_header=8,skip_footer=1)[mkup]
    
    if path.ERRMOD == 2 : #LOS ERROR PLOT    
        #get Insar data
        #reinterpolate los on the choosen mesh
        insar.lossol(path.TCK1, path.step(it,"mesh"), path.LOS1)
        insar.lossol(path.TCK2, path.step(it,"mesh"), path.LOS2)
        tcks=[path.LOS1,path.LOS2]
        angles = [(path.HEA1,path.INC1),(path.HEA2,path.INC2)]
        art.fig.suptitle(f"DMR  Plot it {it},best it {bestit}, errmin {El.min()}, nit tot {nit}")
        for tck,an in zip(tcks,angles) :
            #plot data
            dat=np.genfromtxt(tck,skip_header=8)[mkup]
            mkout = dat!=-99.0
            vmin = np.min(dat[mkout])
            vmax = np.max(dat[mkout])
            # art.plot_shaded_dem()
            cm=art.plot_simple(loc[mkout], dat[mkout],cmap="turbo",vmin=vmin,vmax=vmax)
            art.plot_LOS_arrows(an[0])
            art.ax.set_title(f"Data {tck}")
            art.switch_ax()
            
            #plot model
            losf = LOS_set(an[0],an[1])
            modlos = losf(modu[:,0],modu[:,1],modu[:,2])
            # art.plot_shaded_dem()
            art.plot_simple(loc[mkout], modlos[mkout] ,cmap="turbo",vmin=vmin,vmax=vmax)
            art.ax.set_title("Model")
            art.switch_ax()
            
            #plot residuals
            cm=art.plot_simple(loc[mkout], dat[mkout]-modlos[mkout],cmap="turbo",vmin=vmin,vmax=vmax)
            # art.plot_shaded_dem()
            art.fig.colorbar(cm,label="LOS (mm)",location="right")
            art.ax.set_title("Residuals")
            art.switch_ax()
            
        
    elif path.ERRMOD == 1: #SYNTHETIC DATA ERROR PLOT
        # get synthetic data
        tmp = path.OUTANA
        path.OUTANA = 0
        mechtools.error(path.step(it,"mesh"),path.step(it,"u.sol"))
        path.OUTANA=tmp
        #modeled disp
        obju = np.genfromtxt(path.OBJDISP,skip_header=8,skip_footer=1)[mkup]
        ncomp = ["X","Y","Z"]
        for comp in range(3) :
            pass
            
    


# TODO : create animation of 

plot_conv(save=1)


print("**********************************************")
print("**************    End of Plot   **************")
print("**********************************************")
