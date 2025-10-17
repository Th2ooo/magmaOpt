#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 17:00:20 2024

@author: th2o
"""

import numpy as np


import os
from pathlib import Path

from datetime import datetime as dt
import time
import scipy as sc
from pathlib import Path



class Extent() :
    """Usefull to carry informations about a box domain and make operations
    without having to define them each time theyr are needed"""
    
    def __init__(self,p_min=None,p_max=None) :
        """
        Initialize the domain with the two extreme points

        Parameters
        ----------
        p_min :  arraylike
            the point with the smallest coordinates, format x,y,z
        p_max :  arraylike
            the point with the biggest coordinates, format x,y,z
        """
        if p_min is None :
            #can be intialized with nothing
            return None
            
        
        self.p_min = np.array(p_min)
        self.p_max = np.array(p_max)
        
        
        self.xmin = self.p_min[0]
        self.ymin = self.p_min[1]
        
        
        self.xmax = self.p_max[0]
        self.ymax = self.p_max[1]
        
        self.xrange = abs(self.xmax-self.xmin)
        self.yrange = abs(self.ymax-self.ymin)
        
        self.ranges = [self.xrange,self.yrange]
        
        if len(p_min) == 2 :
            self.zmin = None
            self.zmax = None
            self.depth = None
        else :
            self.zmin = self.p_min[2]
            self.zmax = self.p_max[2]
            self.depth = abs(self.zmin)
            self.zrange = abs(self.zmax-self.zmin)
            self.vol = self.xrange*self.yrange*self.zrange
            self.ranges += [self.zrange]
        
        
        self.ranges = np.array(self.ranges)
        
        
        
        
        self.diago = np.linalg.norm(self.p_max-self.p_min)
        
    def __repr__(self):
        ch=f"Extent of range : x{self.xrange}, y{self.yrange},dpth{self.depth}\n"
        ch += f"X bounds : {self.xmin}, {self.xmax}\n"
        ch += f"Y bounds : {self.ymin}, {self.ymax}\n"
        ch += f"Z bounds : {self.zmin}, {self.zmax}"
        
        return ch
        
    
    def init_with_arr(array) :
        """TODO if usefull, cf 
        data_bounds = Extent(
            [min(gnss_locs[:,0].min(),insar_locs[:,0].min()),
             min(gnss_locs[:,1].min(),insar_locs[:,1].min()),0],
            [max(gnss_locs[:,0].max(),insar_locs[:,0].max()),
             max(gnss_locs[:,1].max(),insar_locs[:,1].max()),2e3])"""
        pass
    
    def init_with_range(self,xrange,yrange,zrange=None) :
        if zrange is not None :
            pmin = [-xrange/2,-yrange/2,-zrange]
            pmax = [xrange/2,yrange/2,0]
        else :
            pmin = [-xrange/2,-yrange/2]
            pmax = [xrange/2,yrange/2]
        self.__init__(pmin,pmax)
    
    def enlarge(self,step) :
        """Increase Extent size in all the directions
        if step scalar,  same for all directions
        if array, choose extension depending on direction"""
        p_min = np.array([self.xmin,self.ymin,self.zmin])-step
        p_max = np.array([self.xmax,self.ymax,self.zmax])+step
        if (type(step) is float) or (type(step) is int) :
            p_max[2] -= step
        else :
            p_max[2] -= step[2] #not enlarging z direction
        self.__init__(p_min,p_max)
        
    def dilate(self,coef) :
        p_min = np.array([self.xmin,self.ymin,self.zmin])*coef
        p_max = np.array([self.xmax,self.ymax,self.zmax])*coef

        self.__init__(p_min,p_max)
        
    def point_in(self,point) :
        """Return wether if the point is in the extent or not"""
        res = (point[0] >= self.xmin  and point[0] <= self.xmax)
        res = res and (point[1] >= self.ymin  and point[1] <= self.ymax)
        if self.zmin is not None :
            res = res and (point[2] >= self.zmin  and point[2] <= self.zmax)
        return res
         
    
    def copy(self) :
        return Extent(self.p_min,self.p_max)
    # def generate_grid(step) :
        
        
        
class McTigueSol :      
    """Class providing utility functions to get the displacement field resulting
    from a McTigur source (finite sphere)"""
    
    def __init__(self,xs,ys,dpth,R,DP,E,nu) :
        """Init the model by defining its main parameters :
            position (xs,ys)
            depth (dpth)
            radius (R)
            pressure change (DP)
            elastic parameters (E,nu)"""
        

        G = E/(2+2*nu) #shear modulus (Pa)


        ## Mc Tigue spherical source model
        
        #Constants for derivation
        A = R**3*DP*(1-nu)/G
        B = (R/dpth)**3
        C = (1+nu)/(-14+10*nu)
        D = 15*dpth**2*(nu-2)/(4*(-7+5*nu))


        #distance to source
        fTiR = lambda x,y : ((x-xs)**2+(y-ys)**2+dpth**2)**.5
        
        
        #constant before disp common to all components
        fTiCte  = lambda x,y : A*(1+B*(C+D/fTiR(x,y)**2)) # A*(1+B)*(C+D/fTiR(x,y)**2)  or  A*(1+B*(C+D/fTiR(x,y)**2)) = good option
        
        #Components of the surface displacement
        self.Ux = lambda x,y : fTiCte(x,y)*(x-xs)/fTiR(x,y)**3
        self.Uy = lambda x,y : fTiCte(x,y)*(y-ys)/fTiR(x,y)**3
        self.Uz = lambda x,y : fTiCte(x,y)*dpth/fTiR(x,y)**3

        


def dist(pt1,pt2) :
    "distance between two points as str"
    pt1 = np.asarray(pt1.split(" "),dtype=float)
    pt2 = np.asarray(pt2.split(" "),dtype=float)
    distn = np.sum((pt1-pt2)**2)**0.5
    return distn

def dipangle(pt1,pt2) :
    "angle to vertical for two points defined as str"
    pt1 = np.asarray(pt1.split(" "),dtype=float)
    pt2 = np.asarray(pt2.split(" "),dtype=float)
    vec = (pt2-pt1)
    norm = np.sum(vec**2)**0.5
    
    ang = np.asin(abs(vec[2]/norm)) #sin=vertical/norm vector
    ang *= 180/np.pi
    return ang
    
        
        
###Usefull functions for computations        

def cart_to_cyl(x,y,z,chx,chy,chz) :
    """Convert a 3D field (chx, chy, chz)
    in a cartesian frame (x,y,z) to a 3D field (chur,chuth,chuz) 
    in a cylindrical frame (r,th,z)
    !!! origins of the frames must be the same
    """
    r = (x**2+y**2)**.5
    costh = x/r
    sinth = y/r
    chur = chx*costh+chy*sinth
    chuth = -chx*sinth+chy*costh
    chuz = chz
    return chur, chuth, chuz









#### INSAR TOOLS

def LOS_set(heading,inclinaison) :
    """Setup an LOS conversion function"""
    hea = heading
    inc = inclinaison
    LOS = lambda E,N,U : -np.cos(hea)*np.sin(inc)*E + np.sin(hea)*np.sin(inc)*N + np.cos(inc)*U
    # LOS = lambda E,N,U : np.cos(hea)*np.sin(inc)*N - np.sin(hea)*np.sin(inc)*E + np.cos(inc)*U CACA

    return LOS


def toYearFraction(int_date):
    """(from StackOverflow) : convert an int date format yyyymmdd
    into float decimal year format"""
    def sinceEpoch(date): # returns seconds since epoch
        return time.mktime(date.timetuple())
    s = sinceEpoch
    # print(int_date)
    date = str(int_date)
    date = dt(int(date[0:4]),int(date[4:6]),int(date[6:]))
    
    year = date.year
    startOfThisYear = dt(year=year, month=1, day=1)
    startOfNextYear = dt(year=year+1, month=1, day=1)

    yearElapsed = s(date) - s(startOfThisYear)
    yearDuration = s(startOfNextYear) - s(startOfThisYear)
    fraction = yearElapsed/yearDuration

    return date.year + fraction


def InSAR_LOS_TS(ifg_dir,locs) :
    """From an InSAR folder extract the time series for each given localisation
    ifg_dir : folder with the raw csv insar data
    locs : list of localisations (EYJA format) for the time series generation
    
    Returns :
        dates of each interferogram (time array of the ts plot) (shape = nb ifg)
        LOS disp values for each dates (shape = (nb locs, nb dates))
        nb of ps used for computation of disp for each localisation  (shape = nb locs)
    """
    ifg_dir = Path(ifg_dir)
    ## get interferogrames dates
    ifg_dates = np.genfromtxt(ifg_dir/"date.txt",dtype=float)
    ifg_dates= ifg_dates.astype(int)
    ifg_dates = np.array([toYearFraction(ind) for ind in ifg_dates])

    nb_loc = len(locs)
    stat_insarlosdisp = np.zeros((nb_loc,len(ifg_dates))) #insar los disp for each station
    stat_nps =  np.zeros((nb_loc),dtype=int) #number of ps for each localisation
    
    ## get ps positions
    insar_latlon = np.genfromtxt(ifg_dir/"ps_ll.txt",dtype=float)
    gg = Geographer()
    insar_latlon[:, [1, 0]] = insar_latlon[:, [0, 1]] #swap columns pour avoir lat lon format
    insar_latlon = gg.WGS84ll_to_ISN94xy(insar_latlon)
    insar_latlon = gg.ISN94xy_to_EYJA(insar_latlon)
    
    ## get the indexes of the ps which are the closests from the localisations
    tree = sc.spatial.KDTree(insar_latlon)
    n_neigh = 200 #number of ps requested
    max_dist = 50 #m , max distance of neighbors
    ## distances to ps and indexes of those ps. Check to see nb ps
    stat_psdists, stat_psindexs = tree.query(locs[:,:2],k=n_neigh,distance_upper_bound=max_dist)

    ##get ifg files
    ifg_files = [n for n in os.listdir(ifg_dir) if "ps_u" in n ]
    ifg_files = sorted(ifg_files,
                       key=lambda name: int("".join([c for c in name if c.isdigit()])))
    
    for idate,file in enumerate(ifg_files): #for each date / ifg file
        print(file)
        #list of displaments of all ps at date i
        disps_datei_allps = np.genfromtxt(ifg_dir/file,dtype=float,usecols=2) #load only last column of file (diplacement)
        
        #LOS displacement for each station at the current date 
        for  istat, neigh in enumerate(zip(stat_psindexs, stat_psdists)) : # for each station
            ps_indexs, ps_dists = neigh
            mask = ps_dists != np.inf 
            ps_indexs = ps_indexs[mask] # we exlude all index which are not within the radius limit
            disps_datei_neighbors = np.take(disps_datei_allps,ps_indexs) #get displacements for all valids neighbors
            stat_insarlosdisp[istat,idate] = np.mean(disps_datei_neighbors) #get the mean of these
            
            if idate == 0 : stat_nps[istat] = len(ps_indexs) #at the first stat iteration,complete the nb ps table
            

    return ifg_dates,stat_insarlosdisp,stat_nps




def down_pt(locs,data,step,method="mean") :
    """Downsample a point cloud of 2 dim with data on it with a certain step size
        method = "mean" (rough mean of the neighboor points)
                 "invm" (mean wheighted with inverse of distances)
    """
    X_locs = np.arange(locs[:,0].min(),locs[:,0].max(),step)
    Y_locs = np.arange(locs[:,1].min(),locs[:,1].max(),step)
    X_locs,Y_locs = np.meshgrid(X_locs,Y_locs)
    grid_down = np.vstack((X_locs.flatten(), Y_locs.flatten())).T
    
    tree_dat = sc.spatial.KDTree(locs)
    tree_grid = sc.spatial.KDTree(grid_down) #tree of interpolation grid
    grid_copins = tree_grid.query_ball_tree(tree_dat, step) #for eeach grid point, list of the neighboors
    
    locs_down = []
    data_down = []
    for i,co in enumerate(grid_copins) :
        # print(i)
        if len(co) >= 20 :
            locs_down += [grid_down[i]]
            cur_speeds = np.array([data[num] for num in co])
            if method=="mean" : #methode basique
                data_down += [np.mean(cur_speeds)]
            elif method=="invm" : #mean weitghted with the distances in respect to the grid point
                inv_dists = np.array([1/np.linalg.norm(grid_down[i]-locs[ix],2) for ix in co])
                norma = np.sum(inv_dists)
                wght = inv_dists/norma
                data_down += [np.sum(cur_speeds*wght)]
            else :
                raise Exception("Bad method")   

    locs_down = np.array(locs_down)
    data_down = np.array(data_down)
    # print(locs_down)
    return locs_down, data_down



def down_pt_grid(locs,data,step,nneig,method="mean") :
    """Downsample a point cloud of 2 dim with data on it with a certain step size
    but output data is grided. nneig is the number of neighboor under which the
    grid cell is considered as empty
        method = "mean" (rough mean of the neighboor points)
                 "invm" (mean wheighted with inverse of distances)
    """
    Xl = np.arange(locs[:,0].min(),locs[:,0].max(),step)
    Yl = np.arange(locs[:,1].min(),locs[:,1].max(),step)
    Yg,Xg = np.meshgrid(Yl,Xl)
    D = np.zeros((len(Xl),len(Yl))) #grid of the final data
    
    tree_dat = sc.spatial.KDTree(locs)
    for i in range(len(Xl)) :
        for j in range(len(Yl)) :
            x = Xl[i]
            y = Yl[j]
            # print(x==Xg[i,j],y==Yg[i,j])
            co = tree_dat.query_ball_point((x,y),step)
            if len(co) >= nneig :
                cur_speeds = np.array([data[num] for num in co])
                if method=="mean" : #methode basique
                    d = np.mean(cur_speeds)
                elif method=="invm" : #mean weitghted with the distances in respect to the grid point
                    inv_dists = np.array([1/np.linalg.norm(grid_down[i]-locs[ix],2) for ix in co])
                    norma = np.sum(inv_dists)
                    wght = inv_dists/norma
                    d = np.sum(cur_speeds*wght)
            else :
                d=np.nan
                
            D[i,j]=d
    
    Yg,Xg = np.meshgrid(Yl,Xl)
    # print(Xg.shape,D.shape)
    grid = np.stack((Xg,Yg,D),axis=2)
    return grid



    