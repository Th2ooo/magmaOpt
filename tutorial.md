# Tutorial for magmaOpt


## Basic usage

To interact with the code as a standard user, the only file you need to modify is `sources/path.py`. There, you will set all the parameters for your case study. Once it is done, you just need to run `sources/main.py`. Note that this code is in devloppment stage. You are invited to modify the code and test the different parameters of the diverse functions to fit to your specific needs.


### `path.py` parameters

You only need to configure this file if you want to run your own test cases. Here is a short description of what  you can modify, section by section. In the provided state, `path.py` is parametrized to run a test case similar to the one presented section 3.1 of the article.

- `Main paths`: configure where the diverse folder needed for the execution are
- `Labels`: Labels given to the different subsets of the mesh (Omega, Gamma, Gamma_u ...). You don't need to change it unless you have specific needs for the initial mesh.
- `Physical problem parameters`: Here you can define the parameters governing the elastic problem: moduli, loads and geometry. For the extent, note that the coordinate system is cartesian, with the point located at the center of the upper boundary Gamma_u is the origin.
- `Meshing parameters`: Governing parameters for the mesh, used in the construction of the initial mesh and at each remeshing operation by mmg. Note that for the moment, the `INHOM` option ensuring a fine mesh close to the source and a coarse mesh elswhere works when building the initial mesh but is then overriden by the remeshing.
- `Optimization parameters`: parameters governing the shape optimization algorithm.
    - `ERRMOD`: crucial to define which kind of problem your are solving, if you want the objective displacement to be from a synthetic analytic or numerical solution, or from actual InSAR data. 
    - The other parameters govern the descent behavior
- `InSAR parameters`: to provide information about the input data (location, LOS geometry, wheighting ...)
- `Other paths`: to configure external executable paths (!! important to modify before the first run), FreeFem files and location of execution products.



### Outputs and visualisation

During or after the optimization, some tools can be used to visualize the mesh or the convergence progresses.

The scripts `sources/plots.py` and `sources/anim.py` are non destructive on the files generated durng the execution, and can be executed independantly in a separated console as the optimization runs. `plots.py` provides plotting routines to visualize the evolution of different quantities with the iterations (Error, step size, volume ..), the shape found at a certain iteration, the error maps for InSAR data. `anim.py`'s routine can be used to generate a movie of the evolution of the shape during the optimization.

The mesh exchange format used in this project is `.mesh`, for its compatibility with FreeFem and GMSH. To visualize such files generated during the optimization, you can use `medit`. For more advanced visualisation using Paraview, you first need to have files in a compatible format such as `.vtu`. By default, the `sources/elasticity.edp` scripts outputs a `u.vtu` file at each execution that can be used to vizualise the displacement fieds. Other fields can be visualized with Paraview by uncommenting the vtu outputs in the FreeFem scripts.



## Tuning the convergence

Depending on the problem you want to solve, the descent may fall in a local minimum and convergence may be never reached (as detailled in the Supporting Information Text S3 of the corresponding preprint). Here we provide a description of how certain parameters may influence the descent, so you can tune them to (hopefully) reach a satysfing convergence.

### Meshing

Obviously, the finer the mesh, the better. A too coarse mesh may have maning drawbacks. It can blur the  error function by averaging the surface displacement on large elements and artificailly modify its value, especially when the objective field has fine artifacts. A coars discretization can also reduce the freedom of the shape optimization, by preventing the devloppment of features of about the element size, which can be a drawback and create artificial local minima. In the end, it is as usual a tradeoff between accuracy and execution time. In the future, some efforts are planned to parallelize some of the steps in the algorithm (mainly FreeFem computations) to reach faster execution.

**Regularization** The regularization lenght `ALPHA` matters. It is the lenght on which the gradient computed on the shape bounday Gamma is stretched/diffused in the domain D\Omega. If it is too small, may lack smoothness and "regularity", if it is too large, it oversmoothes the gradient and loose fine features. Tuning it can sometimes help when the descent is stuck. See Supporting Information Text S2 for additional details.


### Line search

The line search procedure is crucial to adjust the step size, which has a major influence on the descent behavior. Mainly the interval of allowed values for the step and the multiplier matters, and the maximum iteration of the line search loop can be adjusted from there. A too small step slows down the optimization process and a too large steps leads to dramatic changes at each iteration and slows or prevent the convergence. A large multiplier ensure a rapid adaptation in brutal changes of the objective function, but makes the step size very unstable and leads to parasitc oscillations in the descent. The line search strategy we implemented is based on power increase / decrease of the step, but many exist and can be tested.


### Optimization loop

Overall, the full optimization loop may tuned, with for example dynamic tuning of the abovementioned parameters depending on certain criterions on the objective functions. The optimization loop we provide is basic and works for the first test case presented in the paper, but for more advanced problems, more complex optimization strategies could be more relevant.




## Code structure

TODO

## Usefull links

- Source code github repository page : https://github.com/Th2ooo/magmaOpt
- `sotuto` code paper : https://dapogny.org/publis/sotuto.pdf
- Tutorial on scientific computing introducing many of the concepts used in this work, by Charles Dapogny : https://dapogny.github.io/sctuto/index.html
- Tutorial on parallel computong with FreeFem++ by Pierre Jolivet  : https://joliv.et/FreeFem-tutorial/
- GMSH documentation : https://gmsh.info/doc/texinfo/gmsh.html
- MMG documentation: https://www.mmgtools.org/documentation/documentation_index.html
- Medit documentation : https://www.ljll.fr/frey/logiciels/Docmedit.dir/
- Paraview documentation : https://docs.paraview.org/en/latest/UsersGuide/index.html
