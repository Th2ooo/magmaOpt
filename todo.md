# TODO file for the code **magmaOpt**

*author: Théo Perrot*
*sept-oct 2025*


## Things to fix

plot_dmr in plots to compare data model residuals of insar

inhomogenous meshing
    - mmg find good parameters
    - do tests on convergence
    - add local parameters mmg with DEFAULT.mmg3d file (https://www.mmgtools.org/tutorials/tutorials_parameter_file.htmls)

Insar handle N tracks. either
    - Fix the FreeFem for loops handling
    - Modify adjoint2 in inout to add N insar tracks in adjoint2.edp


TO compute the null test, use a synthetic null dispacement field (as in insar interp) instead of solving elasticity



## Features to add



- General option to activate/deactivate vtu outputs


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
    -remove usless funcs or scripts
    -documentation for functions
        -remove charles way of documenting
    -comment

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

- Compute the volume change of the shape


- Synthetic test with 2sources


- Minimize number of scripts
    - remove artist
    - remove geographer


stats.edp give weird results

insar interpolation on mesh edges of correct value (no zero)

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

