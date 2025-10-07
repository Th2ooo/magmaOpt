#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 14:35:07 2023

@author: th2o
"""

import numpy as np
import matplotlib.patches as ptc
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
from matplotlib.ticker import FormatStrFormatter
import scipy as sc
import rasterio
from sources.utils import Extent
from pathlib import Path
from sources.geographer import xISN16,yISN16



# #### Load shading
# try :
#     shd_rast
# except :
#     print("Artist loading DEM")
#     fpath = Path("/media/th2o/GrosSSD/ARPE_Eyja/eyjaFem/input_data/IslandsDEMv1.0_2x2m_isn2016_shade_70.tif")
#     shd_rast = rasterio.open(fpath)
#     shd_dat = shd_rast.read(1)
    
    
eyjaDEM = Path("/media/th2o/GrosSSD/ARPE_Eyja/eyjaFem/input_data/IslandsDEMv1.0_2x2m_isn2016_shade_70.tif")
svartDEM = Path("/media/th2o/GrosSSD/ARPE_Eyja/shape_optim/magmaOpt/data/shade_svart.tif")
    
           
class Artist :
    """Class for plotting all kind of data.
    - thinked for being able of plotting different infos on the same figure
    - create as much artists as plot needed
    - do not need any superv
    
    """
    
    def __init__(self,nrow=0,ncol=0,extent=None,dem=None,fonts=10) :

        if nrow+ncol == 0 :
            self.fig, self._ax = plt.subplots()
            self.nax = None
            
        else :
            self.fig, self._ax = plt.subplots(nrow,ncol)
            self.nax = 0
            [a.set_aspect("equal") for a in self._ax.flatten()]
            [a.ticklabel_format(style="sci") for a in self._ax.flatten()]
        if dem is not None : #can be defined with or withour dem
            self.dem_grid = dem.dem_grid
            self.dem_list = dem.dem_list
            
            
        if extent is None :
            self.extent = Extent([-20e3,-15e3],[20e3,15e3])
        else : 
            self.extent=extent
        self.fonts=fonts
        
        
        
        
        
    def init_topo(self,step=100,path=eyjaDEM,ori=[xISN16,yISN16]) :
        """Load shading for backrounf hillshades"""
        
        print("Artist loading DEM")
        fpath = path
        shd_rast = rasterio.open(fpath)
        shd_dat = shd_rast.read(1)
        
        ext = self.extent
        ext_data = Extent([shd_rast.bounds.left,shd_rast.bounds.bottom],
                         [shd_rast.bounds.right,shd_rast.bounds.top])

        Xg,Yg = np.meshgrid(np.arange(ext.xmin,ext.xmax,step)+ori[0],
                            np.arange(ext.ymin,ext.ymax,step)+ori[1])

        shades = np.zeros(Xg.shape)
        lshd = 255
        for  i in range(Xg.shape[0]) :
            for j in range(Xg.shape[1]) :
                # print(i,j)
                
                if ext_data.point_in([Xg[i,j],Yg[i,j]]) :
                    row,col = shd_rast.index(Xg[i,j],Yg[i,j])
                    shades[i,j] = shd_dat[row,col]
                    lshd = shd_dat[row,col]
                else :
                    # print(i,j)
                    shades[i,j] = lshd
                    
        self.shades = shades
        

    def switch_ax(self) :
        """For switching plot ax"""
        self.nax += 1
        
    @property
    def ax(self) :
        """return current ax and apply it good properties"""
        if self.nax is None : #if 1 subplot mode
            a = self._ax 
        else : 
            a = self._ax.flatten()[self.nax]
        #appy all properties for correct formating
        a.set_aspect("equal")
        a.xaxis.set_major_formatter(FormatStrFormatter('%.0e'))
        a.yaxis.set_major_formatter(FormatStrFormatter('%.0e'))
        a.tick_params(axis='both', labelsize=self.fonts)
        a.set_xlabel("Easting (m)",fontsize=self.fonts)
        a.set_ylabel("Northing (m)",fontsize=self.fonts)
        
        return a
        
        
    def clear(self) :
        """Clear all the plots to use the same Artist object again"""
        plt.close("all")
        self.fig, self._ax = plt.subplots()
        
        
        
    def plot_scatter_dem(self,dem_list) :
        """DEPRECATED (old)"""
        dem_lamb_plt = dem_list    
        fig, ax = self.fig, self.ax

        cs = ax.scatter(dem_lamb_plt[:, 0], dem_lamb_plt[:, 1],
                        c=dem_lamb_plt[:, 2], cmap='terrain')
        fig.colorbar(cs, label="Elevation (m)")    
        ax.set_xlabel("West - East (m)")
        ax.set_ylabel("South - North (m)")
        
        
    def plot_heatmap_dem(self,dem_grid) :
        """DEPRECATED (old)"""
        fig, ax = self.fig, self.ax
        DEM = dem_grid  # variables connsidérée
        
        cs = ax.contour(DEM[:,:,0], DEM[:,:,1], DEM[:,:,2], 15, linewidths=0.5, colors='k')
        cs = ax.contourf(DEM[:,:,0], DEM[:,:,1], DEM[:,:,2], 15, cmap=plt.cm.terrain)
    
        fig.colorbar(cs, label="Elevation (m)")

        ax.set_xlabel("West - East (m)")
        ax.set_ylabel("South - North (m)")
        plt.show()



    def plot_stations(self,stat_pos=None, stat_names=None) :
        """DEPRECATED (old)"""
        fig, ax = self.fig, self.ax
        if stat_pos is not None :
            ax.scatter(self.stat_pos[:, 0], self.stat_pos[:, 1], s=200, color="red")
            if stat_names is not None :    
                for i, name in enumerate(self.stat_names):
                    ax.annotate(name, (self.stat_pos[i, 0], self.stat_pos[i, 1]))  
        ax.scatter(0, 0, color="blue", marker="^")


    def plot_shaded_dem_old(self,alpha) :
        """Plot the shaded dem from grid data, DEPRECATED (old)"""
        fig, ax = self.fig, self.ax
        X,Y,Z = self.dem_grid[:,:,0], self.dem_grid[:,:,1], self.dem_grid[:,:,2]
        ## Plot shaded topography
        light = LightSource(azdeg=315, altdeg=45)
        shades = light.shade(Z,plt.cm.gray, blend_mode="hsv")

        # ax.imshow(shades, cmap=clr, interpolation='nearest')
        ax.contourf(X,Y,shades[:,:,0],levels=100,cmap=plt.cm.gray,aplha=alpha)
        # ax.set_title('Shaded Topography')
        ax.set_xlabel("West - East (m)")
        ax.set_ylabel("South - North (m)")
        
        
    def plot_shaded_dem(self,ext=None) :
        """ Plot shaded dem from source """
        ext = self.extent
        self.ax.imshow(self.shades,cmap="gray",origin="lower",interpolation='bicubic',
                       extent=[ext.xmin,ext.xmax,ext.ymin,ext.ymax])
        
          
    
    def plot_contourf(self,points,data,**kwargs) :
        """Plot points on a continuous color field (with grid interpolation 
        first)"""
    
        fig, ax = self.fig, self.ax
        X,Y = self.dem_grid[:,:,0], self.dem_grid[:,:,1]
        grided_data = sc.interpolate.griddata(
            points[:,0:2],data,(X,Y),method="cubic")[:,:,0]
        
        print(grided_data.shape)
        print(X.shape)
        print(points[:,0].shape)
        contr = ax.contourf(X,Y,grided_data,cmap=plt.cm.coolwarm,alpha=alph,levels=100)
        ax.set_title(title)
        
        # for c in contr.collections:
        #     c.set_alpha(alph)
        return contr
    
    
    def plot_scatter(self,points,data,alph=0.8,cmap="jet_r") :
        """Plot point cloud with colors"""
        
        fig, ax = self.fig, self.ax
        scat = ax.scatter(points[:,0], points[:,1],s=1,
                        c=data, cmap=cmap,alpha = alph) 
        return scat
        
    
        
        
    def plot_simple(self,points,data,interp=False,cmap="coolwarm", **kwargs) :
        """Plot simply scatter data"""
        fig, ax = self.fig, self.ax
        if len(points.shape) == 2 and not interp :
            cs = ax.scatter(points[:,0], points[:, 1],
                            c=data,marker=".", cmap=cmap,**kwargs)
        elif len(points.shape) == 2 and interp :
            X = np.linspace(points[:,0].min(),points[:,0].max(),100)
            Y = np.linspace(points[:,1].min(),points[:,1].max(),100)
            X,Y = np.meshgrid(X,Y)
            grided_data = sc.interpolate.griddata(
                points[:,0:2],data,(X,Y),method="cubic")
            cs = ax.contourf(X,Y,grided_data,cmap=cmap,**kwargs)
            # cs = ax.colormesh(X,Y,grided_data,cmap=plt.cm.coolwarm)
            
        else :
            cs = ax.contourf(points[:,:,0],points[:,:,1],data,cmap=cmap)
            
        # fig.colorbar(cs, label=label)
        return cs
        
        
    def plot_arrows(self,points,data,unc=None,scale=100e3,legscale=1e-2,unit="cm", col=0) :
        """Data must be 3-dimensionnal. 2 first components are considered horizontal
        and the following one is vertical
        Data must be in format Easting,NOrthing, Up"""
        
        fig, ax = self.fig, self.ax
        colo = [["green","blue"],["orange","red"],["magenta","cyan"],["red","blue"]]
        
        for i in range(len(points)) : 
            coor,disp = points[i],data[i]
            dU = disp*scale
            ax.arrow(coor[0],coor[1],dU[0],dU[1],color=colo[col][0],
                     lw=3,
                     length_includes_head=True,head_width=80,zorder=2)
            if unc is not None :
                dUu = unc[i]*scale #scaled uncertainty
                ell = ptc.Ellipse((coor[0]+dU[0],coor[1]+dU[1]), dUu[0], dUu[1],edgecolor=colo[col][0],
                                  fill=False,
                                  lw=2,zorder=1)
                ax.add_patch(ell)
            if len(disp) == 3 :
                ax.arrow(coor[0],coor[1],0,dU[2],color=colo[col][1],
                         lw=3,
                         length_includes_head=True,head_width=80,zorder=2)  #vertical component plot
                if unc is not None :
                    ell = ptc.Ellipse((coor[0],+coor[1]+dU[2]), dUu[2], dUu[2],edgecolor=colo[col][1],
                                      fill=False,
                                      lw=2,zorder=1)
                    ax.add_patch(ell)
        
        ax.text(ax.get_xbound()[0]+3e3,ax.get_ybound()[1]-3e3,"1"+unit,fontsize='x-large',fontweight="heavy",color="red")
        ax.arrow(ax.get_xbound()[0]+2e3,ax.get_ybound()[1]-3e3,0,scale*legscale,color="red",lw=5,length_includes_head=True,head_width=20)
        # fig.show()
        
        
    def plot_texts(self,points,texts,**kwargs) :
        """Usefull to plot station names or comments"""
        if "color"  in kwargs.keys() : c = kwargs["color"]
        else : c ="yellow"
        if "backgroundcolor"  in kwargs.keys() : bc = kwargs["backgroundcolor"]
        else : bc ="black"
        
        fig, ax = self.fig, self.ax
        for coor,txt in zip(points,texts) :
            if len(coor) == 3 :
                x,y,_=coor
            else :
                x,y = coor
            
            ax.text(x,y,txt,**kwargs)
            
    def plot_LOS_arrows(self,hea,scale=1e3) :
        """Plot arrows defining LOS geometry
        hea : heading"""
        fig, ax = self.fig, self.ax
        scale = 2e3
        ax.arrow(ax.get_xbound()[0]+4e3,ax.get_ybound()[1]-4e3,
                 scale*np.sin(hea),scale*np.cos(hea),color="black",lw=5)
        ax.arrow(ax.get_xbound()[0]+4e3,ax.get_ybound()[1]-4e3,
                 (scale-1e3)*np.sin(hea-np.pi/2),(scale-1e3)*np.cos(hea-np.pi/2),color="black",lw=5)
        



            
    def show(self) :
        
        self.fig.show()
        
                

        
        

    

    
if __name__=="__main__" :
    
    
    pass
    # ext = Extent([-20e3,-5e3,0],[10e3,5e3,0])
    
    # ext = Extent([data.bounds.left,data.bounds.bottom,0],
    #                  [data.bounds.right,data.bounds.top,0])
    

    # ext.enlarge(-1e3)
    # stp = 100
    # Xgl = np.arange(ext.xmin,ext.xmax,stp)
    # Ygl = np.arange(ext.ymin,ext.ymax,stp)
    # Xg,Yg = np.meshgrid(Xgl,Ygl)
    
    # shades = np.zeros(Xg.shape)

    # for i,xgl in enumerate(Xgl) :
    #     for j,ygl in enumerate(Ygl) :
    #         # print("Eyja",xgl,ygl)
    #         # x,y = EYJA_to_ISN16xy([xgl,ygl])
    #         # print("ISN16",x,y)
    #         # print(xgl,ygl)
    #         row,col = data.index(xgl,ygl)
            
    #         shades[i,j] = el[row,col]
    #         # print(i)
    #     #     break
    #     # break

        
    # plt.imshow(shades,extent=[ext.xmin,ext.xmax,ext.ymin,ext.ymax],origin="lower")
    # # plt.contourf(Yg,Xg,shades,levels=100,cmap="gray")
    # x = np.array(range(data.shape[0]))*data.transform.a + data.transform.c
    # y = np.array(range(data.shape[1]))*data.transform.e + data.transform.f

    # x_dat,y_dat = np.meshgrid(x,y)
    
    # plt.contourf(x,y,el,levels=100,cmap="gray")
    
    
    