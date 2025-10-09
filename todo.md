# TODO file for the code **magmaOpt**




## Things to fix


- Minimize number of scripts
    - remove artist
    - remove geographer
    - merge error and adjoint different scripts


inhomogenous meshing
    - mmg find good parameters
    - do tests on convergence

stats.edp give weird results


## Features to add

- InSAR data improvement :
    instead of nearest neighbor interpolation, hande no data points
    -> select a no data value and put it in insar.py
    -> then modify error and adjoint to ignor no data points in integrals


- Bigger domains simulation for geophysics application
    - Paralellizing option for speed-up
        1. Freefem codes : petsc+mpi (https://joliv.et/FreeFem-tutorial/section_8/example8.edp.html)
            - elasticity
            - adjoint
            - gradE
        2. mmg3d : parmmg (https://github.com/MmgTools/ParMmg/tree/master)
        3. GMSH meshing



- Move all path managments  to Pathlib


- Clean code

- proper Readme
    - install instructions
    - licence
    - screenshots

- Improve Line Search (https://optimization.cbe.cornell.edu/index.php?title=Line_search_methods)
    - check for better adaptation of step size algorithms
    - Add more clever step size (coef) managment, using previous error/coef behavior
    - accelerate if slow descent
    - stay steady if good descent
    - slows if flat




## Done


- REGLS regularization nessecary ?


- LOS error
    - working with real data ?
    - fix adjoint


- External data :
    - Hande N data sources
    - InSAR
        - be able to get data from any cartesian coordinate system (no internal conversion)
        - automatically compute the center of  the data to optionally input it only
        - dont interpolate at each iteration in insar func, only do it in error and adjoint



- Saving outputs of a run in separate folder

- GMSH meshing
    - speration line to remove on source (not a big deal, not causing bugs)
    - point alone on the top of the source which stays if steps are not big enough

- Remote git repo

- Dimensionalization
    - Small steps when redimensionallizing
        - Pressure ?
        - Lenght ?
        - Step size ?
    - Normalizing Error ?
    - Coeff managment

- Alpha in regularization coeff

- Gradient inn descent should be normalized to avoid inappropriate step size


- Manage inhomogenous element sizes meshes for bigger domain simulation
    - Inhomogeneous mesh size for larger domains simulation (coarse far, fine close source)
        - Modify GMSH meshing
        - Test if mmg works well

