#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 29 11:14:27 2025

@author: th2o
"""

import shutil
from pathlib import Path
import sources.path as path
from datetime import datetime
import numpy as np


def save_results(name="") :
    """
    Save the results after execution

    Returns
    -------
    None.

    """
    if not name :
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        name = f"{timestamp}"
        
    dest = Path(path.RUNS)/name
    dest.mkdir(parents=True,exist_ok=True)
    
    # save plots files
    origin = Path(path.PLOTS)
    for f in origin.iterdir() :
        if f.is_file() :
            print(f)
            shutil.copy2(f,dest)
      
    # get best iteration
    histo = np.genfromtxt(path.HISTO,delimiter=" ")
    errl = histo[:,1] #errors
    bestit = int(np.argmin(errl))
    
    # save res flies
    origin = Path(path.RES)
    to_save = ["path.data","exch.data","histo.data",f'step.{bestit}.mesh',f'step.{bestit}.u.sol']
    for f in origin.iterdir() :
        if f.is_file() and f.name in to_save :
            print(f)
            shutil.copy2(f,dest)
            
            
            
             
    print("Results and vizualisations saved in",dest)
    
        
        
if __name__ == "__main__" :
    
    
      save_results("insar_test3_best")
    