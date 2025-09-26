#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  7 15:49:31 2023

@author: th2o
"""

import scipy as sc
import numpy as np

import matplotlib.pyplot as plt


import pyproj
import os
import rasterio

# from utils import Extent
from pathlib import Path


#### Geographer functions

"""General functions to process all spatialized data

References models :
    WGS84latlon : global ref frame comonly used, degrees (geographic)
    WGS84xyz : idem but center of earth = origin, meters (cartesian)
    ISN94 : xy system referenced on Iceland
    ISN16 : latlon system referenced on Iceland
    Esja : personnalised ref system, ISN94 translated on Eyja summit

TODO :
    -check input DEM (ISN94/WGS984xyz,/WGS)
    -check if given heights are ellipsoidal or topographic heights
  """
    
    
##Coordinates of the EYJA coordinate system : 
##    ISN94 tranlslated to the point (xISN94,yISN94,0)
##OR  ISN16 tranlslated to the point (xISN16,yISN16,0)
## xISN,yISN being a local origin taken at Eyjafjallajökull summit position

#summit position in WGS84
latWGS84 = 63.6207009
lonWGS84 = -19.61574326
#summit position in ISN94
xISN94 = 469457.2243750986 #EAST
yISN94 = 346379.9939689741 #NORTH
#summit position in ISN16
xISN16 = 2669457.2243751 #EAST
yISN16 = 146379.99396897 #NORTH

#Got after after doing
# ori14 = ISN94xy_to_WGS84ll([[xISN94,yISN94]])
# ori16 = WGS84ll_to_ISN16xy(ori14)


# Below dont work
# fpath = Path("/media/th2o/GrosSSD/ARPE_Eyja/eyjaFem/data/IslandsDEMv1.0_2x2m_zmasl_isn2016_70.tif")
# data = rasterio.open(fpath)
# el = data.read(1)
# data.transform*np.unravel_index(np.argmax(el),el.shape)
        

    
def coor_to_pos_rid(arr):
    """Transform an array of type [LAT,LONG,EL] in 3D positions (
    basic geometry operation, inaccurate) marche """
    r = 6371e3  # earth's radius (m)
    arr[:, 0:2] *= np.pi/180*r
    return arr


def coor_to_pos_basic(arr):
    """Transform an array of type [LAT,LONG,EL] in 3D positions
    origin at the center of the earth assuming earth is a sphere
    marche pas"""
    r = 6371e3  # earth's radius (m)
    arr[:, 0:2] *= np.pi/180
    arr[:, 0] = r*np.cos(arr[:, 0])*np.cos(arr[:, 1])
    arr[:, 1] *= r*np.cos(arr[:, 0])*np.sin(arr[:, 1])
    return arr



def coor_to_pos3d(coor):
    """Transform WGS84 (Lat/Lon) to a 3d geocentric coordinate system
    based on WGS84s"""
    transformer = pyproj.Transformer.from_crs(
        "EPSG:4326", "EPSG:4978", always_xy=True)
    xyz = transformer.transform(coor[:, 0], coor[:, 1], coor[:, 2])
    return np.array(xyz).transpose()



def WGS84ll_to_ISN94xy(coor):
    """Transform WGS84 lonlat (world coordinate system on ellipsoid unprojected) to
    ISN94 xy (iceland coordinate system with lambert projection)
    !!coor must have only 2 columns
    !!coor[:,0] latitude, coor[:,1] longitude"""
    transformer = pyproj.Transformer.from_crs(
        "EPSG:4326", "EPSG:3057")
    lat,lon = coor[:, 0], coor[:,1]
    xy = transformer.transform(lat,lon)
    return np.array(xy).transpose()


def WGS84ll_to_ISN16xy(coor):
    """Transform WGS84 lonlat (world coordinate system on ellipsoid unprojected) to
    ISN16 xy (iceland coordinate system with lambert projection)
    !!coor must have only 2 columns
    !!coor[:,0] latitude, coor[:,1] longitude"""
    transformer = pyproj.Transformer.from_crs(
        "EPSG:4326", "EPSG:8088")
    lat,lon = coor[:, 0], coor[:,1]
    xy = transformer.transform(lat,lon)
    return np.array(xy).transpose()


def ISN94xy_to_WGS84ll(coor):
    """Transform WGS84 lonlat (world coordinate system on ellipsoid unprojected) to
    ISN94 xy (iceland coordinate system with lambert projection)
    !!coor must have only 2 columns
    !!coor[:,0] latitude, coor[:,1] longitude"""
    transformer = pyproj.Transformer.from_crs(
        "EPSG:3057", "EPSG:4326")
    coor = np.array(coor)
    x,y = coor[:, 0], coor[:,1]
    latlon = transformer.transform(x,y)
    return np.array(latlon).transpose()


def ISN94xy_to_EYJA(coor) :
    """Transform ISN94 coordinates to the so-called EYJA coordinate system :
        - same coordinates
        - origin translated to a point located on the summit of 
        eyjafjallajokull but at sea level 
            O = (xISN,yISN,0.0)
        !! dont modify elevation
        !! coor must have only 2 columns
    """
    process = np.array(coor)
    process -= np.array([xISN94,yISN94])
    return process



def EYJA_to_ISN94xy(coor) :
    """Switch the other way around
    !! dont modify elevation"""
    coor = np.array(coor)
    if coor.shape[1] == 2 :            
        coor += [xISN94,yISN94]
    elif coor.shape[1] == 3 : 
        coor += [xISN94,yISN94,0]
    return coor
    

def ISN16xy_to_EYJA(coor) :
    """ Idem with ISN16"""
    coor = np.array(coor)   
    coor -= np.array([xISN16,yISN16])
    return coor


def EYJA_to_ISN16xy(coor) :
    """Switch the other way around
    !! dont modify elevation"""
    a = np.array(coor)
    a += np.array([xISN16,yISN16])
   
    return a







class Topographer() :
    """Generate or load DEMs"""
    
    def __init__(self,secretary,extent=None,S=None,N=None,path=None) :
        """Different ways of initialize a topographer :
            
            - files : dict {}
            - opt = "load" load an existing DEM depending on the filename :
                fpath = path to the desired dem
            - opt = "new" create a DEM from the original raw file
                fpath : path of the raw original dem
                kwargs :
                    xrange = range in the x direction
                    yrange = range in the y direction
                    step = see self.downsample_dem() args
                    num = see self.downsample_dem() args
            - opt = initialize an empty Topographer
            
        """
        
        self.sec = secretary #to handle files
        self.str_opt = "" # string for automatic naming files
        
        #Extent of the DEM : rectangle of edges (xmin,ymin),(xmax,ymax)
        self.xmin = None
        self.ymin = None
        self.xmax = None
        self.ymax = None
        


        if extent is not None :
            
            self.xmin = extent.xmin
            self.ymin = extent.ymin
            self.xmax = extent.xmax
            self.ymax = extent.ymax
            
        
            
    def init_with_file(self,path,extent,S,N) :
        """Initialize the dem giving a file in order to not reprocess if 
        already has been processed"""
        
        path = self.sec.get_file(path) #get the full path
        
        if path.is_file() : #if dem already has been created
            self.load_dem_grid(path)
        else : #intialize it otherwise
            self.__init__(self.sec,extent)
            self.get_originial_dem(self.sec.get_file("demraw"))
            self.downsample_dem(S,N)
            self.save_dem_grid(path)
  
             
        
    def __repr__(self) :
        """Display function"""
        ch = '***Object Topographer***\n'
        ch += f"W/E length :{abs(self.xmin-self.xmax)}m \n"
        ch += f"S/N length :{abs(self.ymin-self.ymax)}m \n"
        ch += f"xmin {self.xmin}, xmax {self.xmax} \n"
        ch += f"ymin {self.ymin}, ymax {self.ymax}\n"
        ch += f"{self.dem_grid.shape[0]} points x axis, {self.dem_grid.shape[1]} points y axis"
        return ch
        

        
    def load_dem_list(self,fpath) :
        """Load a processed DEM, list format"""
        dem_list = np.genfromtxt(fpath, dtype=float, delimiter=";")
        self.dem_list = dem_list
        self.xmin = dem_list[:,0].min()
        self.xmax = dem_list[:,0].max()
        self.ymin = dem_list[:,1].min()
        self.ymax = dem_list[:,1].max()
        self.dem_grid = self.list_to_grid(self.dem_list)
        
        
    def load_dem_grid(self,fpath) :
        """Load a processed DEM, grid format"""
        with rasterio.open(fpath, 'r') as src:
            X = src.read(1)
            Y = src.read(2)
            Z = src.read(3)
        self.dem_grid = np.dstack((X,Y,Z))
        self.xmin = X[:,0].min()
        self.xmax = X[:,0].max()
        self.ymin = Y[0,:].min()
        self.ymax = Y[0,:].max()
        self.dem_list = self.grid_to_list(self.dem_grid)
        
        
        
    def grid_to_list(self,grid) :
        """Convert a grid X,Y,Z (shape = [nx,ny,3]) 
        to a list (shape [nx*ny,3])"""
        X,Y,Z = grid[:,:,0],grid[:,:,1],grid[:,:,2]
        lis = np.vstack([X.ravel(), Y.ravel(), Z.ravel()]).transpose()
        return lis
    


    def list_to_grid(self,lis):
        """Convert a list (shape [nx*ny,3]) 
        to a grid X,Y,Z (shape = [nx,ny,3])"""
        total_elements = lis.shape[0]
        sqrt_val = int(np.sqrt(total_elements))
        
        for i in range(sqrt_val, 0, -1):
            if total_elements % i == 0:
                M = i
                N = total_elements // i
                break
        # Get unique indices for reshaping
        _, indices = np.unique(np.arange(M * N) // N, return_index=True)
        reshaped_data = np.split(lis, indices)[1:]
        reshaped_data = np.array(reshaped_data).reshape(M, N, -1)
        return reshaped_data



    def get_originial_dem(self,dem_path) :
        """create the dem coordinates from the orignal rough DEM file
        - extract the data from the file
        - switch to lambert coordinate system
        - shift the coordinates to a local origin, the summit of eyja => new coordinate system
        - cropp the dem (xmin,ymin), (xmax,ymax) : edges of the cropping rectangle (in local coordinate system)
        """
        
        dem_dat = np.genfromtxt(dem_path, dtype=float, delimiter=" ")
        dem_dat[:,[0,1]] = dem_dat[:,[1,0]] #switch columns to have lat lon format
        dem_lamb = WGS84ll_to_ISN94xy(dem_dat[:, 0:2])
        dem_lamb = np.column_stack((dem_lamb, dem_dat[:, 2]))
    
    
        amax = dem_lamb[:, 2].max()
        iamax = dem_lamb[:, 2].argmax()
        xamax, yamax = dem_lamb[iamax, 0:2]
        print("Summit position (ISN 93) :", xamax, "E(m)", yamax, "N(m)", amax, "Z(m)")
    
        # move origin to summit position
        dem_lamb[:, 0:2] = ISN94xy_to_EYJA(dem_lamb[:, 0:2])
        dem_init=dem_lamb
        
        mask = (dem_init[:, 0] >= self.xmin) & (dem_init[:, 0] <= self.xmax) & (
            dem_init[:, 1] <= self.ymax) & (dem_init[:, 1] >= self.ymin)
    
        self.dem_init = dem_init[mask]
         
        print(" --- Geoographer.get_original_DEM ::: DEM loaded")



        
    
    def downsample_dem(self,step=None, num=None) :
        """Downsample the dem :
        - reduce the number of points of the dem :
            1 : grid respecting the defined edges with regular step
            2 : grid respecting the defined edges with a certain number of point
            3 : grid not respecting the edges but with a controlled points number
            and step size, centered on (0,0) !! update edges
        - output is in a list format and in a grid format
        
        """
        dem_init = self.dem_init
    
        """Grid creation"""
            
        if (num is None) and (step is not None) : #mode par pas de grille
            X = np.arange(self.xmin, self.xmax, step)  # EAST/WEST axis
            Y = np.arange(self.ymin, self.ymax, step)  # NORTH/SOUTH axis
            
        elif (num is not None) and (step is None) : # mode par nombre de points
            X = np.linspace(self.xmin, self.xmax, num)  # EAST/WEST axis
            Y = np.linspace(self.ymin, self.ymax, num)  # NORTH/SOUTH axis
            
        elif (num is not None) and (step is not None) :
            X = np.array([i*step for i in range(num)]) - (num-1)*step/2
            Y = X.copy()
            self.xmin = X[0]
            self.ymin = Y[0]
            self.xmax = X[-1]
            self.ymax = Y[-1]
        else :
            raise Exception("Invalid input parameters")
        self.str_opt = f"step{step}_num{num}"

        X_grid, Y_grid = np.meshgrid(X, Y)

        print(X_grid.shape)
        """Interpolation method to downsample"""
        # methods linear and cubic reduces the number of points
        # dem_lamb_down[np.logical_not(np.isnan(dem_lamb_down[:,2]))] to filter NaN
        print("zobi")    
        print(dem_init.shape)
        Z = sc.interpolate.griddata(
            dem_init[:, 0:2], dem_init[:, 2], (X_grid,Y_grid), method="nearest")  
        print("zoba")
        self.dem_init = None #release memory
        
        self.dem_grid = np.dstack((X_grid,Y_grid,Z))
        self.dem_list = self.grid_to_list(self.dem_grid)
    

        print(" --- Geoographer.downsample_dem ::: DEM downsampled,",len(self.dem_list),"points")
    

    def load_station_info(self,fpath) :
        raw = np.genfromtxt(fpath, dtype=str, delimiter=";")
        stat_names = raw[:,2]
        stat_pos = np.array(raw[:,0:2],dtype=float)
        self.stat_names =stat_names
        self.stat_pos = stat_pos
         

   
    
    def save_dem_list(self,filename=None) : 
        """Save the computed dem in a list format"""
        header_dem="X (east) [m] ; Y (north) [m] ; Z (elevation) [m]"
        if filename is None :
            filename = "dem_list_"+self.str_opt+".csv"
        np.savetxt(filename,self.dem_list, delimiter=";")
        print(" --- Geoographer.save_dem_list ::: DONE")


    def save_dem_grid(self,filename=None) :
        """Save the computed dem in a grid format"""
        DEM = self.dem_grid
        h, w, d = DEM.shape
        dtype = DEM.dtype  # Type de données pour les valeurs de la grille    
        if filename is None :
            filename = f'dem_{self.str_opt}.tif'
        # Création d'un fichier raster avec rasterio
        with rasterio.open(filename, 'w', driver='GTiff', 
                           height=w, width=w, count=3, dtype=dtype) as dst:
            dst.write(DEM[:,:,0], indexes=1)  
            dst.write(DEM[:,:,1], indexes=2) 
            dst.write(DEM[:,:,2], indexes=3)  
        print(" --- Geoographer.save_dem_grid ::: DONE")
        


        
if __name__=="__main__":

    pass
    # g = Topographer("original_DEM_eyjafjallajökull_with_ice.txt",opt="new",
    #                 xrange=10e3,yrange=10e3,num=500,step=None)
    # g.save_dem_grid()
    # ext = Extent([-10e3,-10e3,0],[20e3,20e3,0])

    # from artist import Artist
    # di = Artist()
    # di.plot_heatmap_dem(g.dem_grid)

