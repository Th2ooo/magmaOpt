# TODO file for the code **magmaOpt**




## Things to fix

- Dimensionalization
    - Small steps when redimensionallizing
        - Pressure ?
        - Lenght ?
        - Step size ?
    - Normalizing Error ?


- LOS error
    - working with real data ?


## Features to add

-GMSH meshing
    - inhomogeneous mesh size for larger domains simulation

- Paralellizing option for speed-up
    1. Freefem codes : petsc+mpi (https://joliv.et/FreeFem-tutorial/section_8/example8.edp.html)
        - elasticity
        - adjoint
        - gradE
    2. mmg3d : parmmg (https://github.com/MmgTools/ParMmg/tree/master)
    3. GMSH meshing




- VTK outputs option in separate folder


- Move path managments  to Pathlib


- Clean code

- Remote git repo



## Done

- Saving outputs of a run in separate folder

- GMSH meshing
    - speration line to remove on source (not a big deal, not causing bugs)
    - point alone on the top of the source which stays if steps are not big enough






