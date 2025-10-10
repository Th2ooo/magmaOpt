#!/usr/bin/pythonw
# -*-coding:Utf-8 -*


"""
author: Théo Perrot (modified from Charles Dapogny and Florian Feppon)

Informations:
   - To run from the console inside the magmaOpt/ folder : python -m sources.main
   - Mesh compatibility problem : export in .mesh format crashes with GMSH 4.14 
       -> Downgrade to GMSH 4.13



Improvements ideas
    - speed up by paralelizing solving
    - object oriented paradigm
    - clean code
    - alow inhomogeneous mesh
    - change mesh bouundaries (half sphere ?)
    
"""

import sys
import os

if 0 : #To activate if called from any other directory than magmaOpt
    # Set working directory to magma/ and add sources to path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    sys.path.insert(0, project_root)

import numpy as np
import subprocess
import sources.path as path
import sources.inout as inout
import sources.extools as extools
import sources.mechtools as mechtools
import sources.basemesh as basemesh
import sources.insar as insar


"""
TODO BEFORE PUBLISHING

    - numerical errror 
    - test insar again


DONE 
    -finsh cleaning merit / gradient calcluation -> DONE
    -recheck signs/code
    -benchmark with Charles code
    - null test systematically
    - commmon output folder for results3
    - prevent mmg to move the cube booundaries :
    - solve dimension problem



    
Usefull links :
    github page : https://github.com/Th2ooo/magmaOpt
    medit doc : https://www.ljll.fr/frey/logiciels/Docmedit.dir/
    sotuto paper : https://dapogny.org/publis/sotuto.pdf
    charles tuto scientific comp : https://dapogny.github.io/sctuto/index.html
    pierre jolivet freefem parralel computing tuto : https://joliv.et/FreeFem-tutorial/
    GMSH doc : https://gmsh.info/doc/texinfo/gmsh.html


"""

restart = 0 #Restart iteration
verb = 0 #Verbosity level
#%% #### Initialization
###############################################################
##################      START PROGRAM    ######################
###############################################################


"""Enter the main optimization loop of magmaOpt"""
   
print("*************************************************")
print("********************* magmaOpt ******************")
print("*************************************************")

if not restart  :    
    # Initialize folders and exchange files
    inout.iniWF()

    # Test the links with external C libraries
    # inout.testLib()
    
    
    ## Creation of the initial mesh
    print("Creating intial mesh")
    basemesh.inimsh(path.step(0,"mesh"),vizu=1,inhom=path.INHOM)
    
    
    ## Initialize error 
    if path.ERRMOD == 0 or path.ERRMOD == 1 : 
        #Evaluate the min of error function -> create a mesh with source located at target solution
        basemesh.inimsh(path.OBJMESH,psrc=[path.XST,path.YST,-path.DEPTH], 
                        rads=[path.RVRAI]*3,vizu=1,inhom=0) #creating mesh of the solution
        
        #Compute the error of this "best" mesh
        e = mechtools.elasticity(path.OBJMESH,path.OBJDISP) # computing its displacement field
        
        if path.ERRMOD == 0 : #Analytical error against mogi soultion of best mesh possible
            bestE = mechtools.error(path.OBJMESH,path.OBJDISP) 
        elif path.ERRMOD == 1 : #Best possible error is 0 bc best mesh exists
            bestE = 0.0 

    elif path.ERRMOD == 2 :
        insar.init(1) # tranfer the insar data into the initial mesh 
    
        
    ## Compute Null test of the best solution
    print("Null test computation ...")
    inout.setAtt(file=path.EXCHFILE,attname="Pressure",attval=0.0) # -> set null pressure to have a 0 disp field
    mechtools.elasticity(path.step(0,"mesh"),path.step(0,"u.sol"))
    nullE = mechtools.error(path.step(0,"mesh"),path.step(0,"u.sol"))
    inout.setAtt(file=path.EXCHFILE,attname="Pressure",attval=path.PRESS) 
    print(f"Null test {nullE}")

        
    if path.ERRMOD == 2 : #if unknow source, null test is the ref
        bestE = nullE

        
    # Resolution of the state equation
    mechtools.elasticity(path.step(0,"mesh"),path.step(0,"u.sol"))
    
    
    # Calculation of the error of the shape
    print("Evaluation of intial error")
    newE  = mechtools.error(path.step(0,"mesh"),path.step(0,"u.sol"))
    curE = newE
    print(f"Minimal error reachable {bestE}")
    print("*** Initialization: Error {}".format(newE))
    
    # Coefficient for time step ( descent direction is scaled with respect to mesh size)
    coef = path.MINCOEF
    # Number of refinement steps
    nref = 0
    
    iniE = newE #Initia0.02l error
    minE = newE
    itstart = 0
    minit = 0
    

else : ## To restart loop at  a given it
    curE = mechtools.error(path.step(restart,"mesh"),path.step(restart,"u.sol"))
    newE=curE
    coef=0.02
    itstart = restart
    bestE = 6.99e02
    minit = 0
    minE = 5e3
    nullE = 0.0



#%% #### Main loop
###############################################################
##################      ITERATIVE LOOP     ####################
###############################################################

"""
At the beginning of each iteration, are available:
   - the mesh lT^n of $D$ associated to the current shape Omega^n;
   - the solution to the linear elasticity equation on $Omega^n$ (at the nodes of $D$).
   - The error of the shape
"""

for it in range(itstart,path.MAXIT) :
    # Change value of tolerance after a certain number of iterations
    # if (( it == 100 ) or (curE+path.ERRTOL<newE)) and False : #no improvement in error (curE=E last it, newE=E cur it)
    #   print("REFINEMENT")
    #   nref += 1
    #   path.TOL  = path.TOL/2
    #   path.HMIN = path.HMIN/2
    #   print(f"New tol {path.TOL}, New hmin {path.HMIN}")
    
    # update best minimum found
    if newE < minE : #new minimum 
        minit = it
        minE = newE
    
    curmesh = path.step(it,"mesh")
    newmesh = path.step(it+1,"mesh")
    curphi  = path.step(it,"phi.sol")
    newphi  = path.step(it+1,"phi.sol")
    curu    = path.step(it,"u.sol")
    curp      = path.step(it,"p.sol")
    newu    = path.step(it+1,"u.sol")
    curEgrad = path.step(it,"E.grad.sol")
    curgrad = path.step(it,"grad.sol")
    curE = newE
    
    print("**************************************************************************************")
    print(f"Iteration {it}: Error {curE:.2E}, Obj {bestE:.2E} (null={nullE}), Coeff {coef:.3f}")
    print("**************************************************************************************")
    
    #Compute stats of the current domain
    vol,barx,bary,barz = mechtools.stats(curmesh)
    #print("STATS", vol,barx,bary,barz)
    
    
    # Print values in the path.HISTO file
    inout.printHisto(it,curE,vol,coef,barx,bary,barz)
    
    # Generation of a level set function for $\Omega^n$ on $D$
    print("  Creation of a level set function")
    extools.mshdist(curmesh,curphi)
    
    print("  Computation of the adjoint state ")
    mechtools.adjoint(curmesh,curu,curp)
    
    print("  Computation of a descent direction")
    # Calculation of the gradient of error
    mechtools.gradE(curmesh,curu,curp,curEgrad,curphi)

    # Calculation of a descent direction
    mechtools.descent(curmesh,curphi,curE,curEgrad,curgrad) 
    
    
    # Line search
    for k in range(0,path.MAXITLS) :
        print(f"  Line search k = {k}; step size = {coef:.2f}")
          
        # Advection of the level set function and smoothing of the resulting LS function
        print("    Level Set advection")
        extools.advect(curmesh,curphi,curgrad,coef,newphi)
        # extools.regls(curmesh,newphi,newphi)
          
          
        # Creation of a mesh associated to the new shape
        print("Local remeshing")
        retmmg = extools.mmg3d(curmesh,1,newphi,path.HMIN,path.HMAX,path.HAUSD,path.HGRAD,1,newmesh) 

        if  not retmmg  :
            print("Error in mmg, end of loop")
            break

        # Resolution of the state equation on the new shape
        print("    Resolution of the linearized elasticity system")
        mechtools.elasticity(newmesh,newu)
      
        # Calculation of the new value of error
        newE = mechtools.error(newmesh,newu)
        print(f"New error {newE:.2E}")

          
        # Decision
        if  ( newE <  curE+path.TOL*abs(curE) )   : # strict improvement in the error
            coef = min(path.MAXCOEF,coef*path.MULTCOEF)
            print("    Iteration {} - subiteration {} accepted\n".format(it,k))
            break
        elif ( newE < curE+path.TOL*abs(curE) ) : # slight increase of error accepted
            coef = coef # no modification of the coe
            print("    Iteration {} - subiteration {} accepted despite slight increase in error\n".format(it,k))
            break
        elif ( k == path.MAXITLS-1 ) or ( coef <= path.MINCOEF )  : # end of LS reached or coeff too low
            coef = min(path.MINCOEF,1*coef)
            print("    Iteration {} - subiteration {} accepted by default, end of line search\n".format(it,k))
            break
        else : # Reject iteration: go to start of line search with a decreased "time step"
            print("    Iteration {} - subiteration {} rejected".format(it,k))
            proc = subprocess.Popen(["rm {nmesh}".format(nmesh=newmesh)],shell=True)
            proc.wait()
            coef = max(path.MINCOEF,coef/(2*path.MULTCOEF))
        
   
        
    if 0 :
        if  ((it-minit) > 100)   : # end the loop if no improvement have been made in a while
            print("No sufficient improvement have been made in a while")
            break
        elif  ((newE-minE)>0.1*iniE):
            print("No sufficient improvement have been made compared to initial guess")
            break
        
    # ## FOR PROFILING ONLY !!!
    # if it > 3 :
    #     break
    
###############################################################
####################       END PROGRAM      ###################
###############################################################

print("*************************************************")
print("****************** End of magmaOpt **************")
print("*************************************************")

    
    
    
