# Tutorial for magmaOpt


## Basic usage

To interact with the code as a standard user, the only file you need to modify is `sources/path.py`. There, you will set all the parameters for your case study. Once it is done, you just need to run **sources/main.py**. Note that this code is in development stage. You are invited to modify the code and test the different parameters of the diverse functions to fit to your specific needs.

To run the code from your virtual environment, activate it, go in the magmaOpt root folder and run
```bash
python -m sources.main
```
If you want to run it from any folder (e.g. with a custom IDLE), you may set the variable `diff_fold` to true in `main.py`.

### **path.py** parameters

You only need to configure this file if you want to run your own test cases. Here is a short description of what you may modify, section by section. In the provided state, `path.py` is parametrized to run a test case similar to the one presented section 3.1 of the article.


- **Files paths** : configure where the diverse folder needed for the execution are.
- **Labels** : labels of the mesh domains and boundaries, modify only if needed.
- **Physical parameters** : Values of the physical quantities of the models, including the parameters of the initial and objective (not used if real data) shapes.
- **Meshing parameters** : configuration of the mesh size and remeshing parameters for mmg. To speed up the iteration time, huge difference between `HMIN` and `HMAX` and higher value for `HGRAD` may be applied, at the cost of important mesh coarsening far from the source or the free surface.
- **Optimization parameters** : key parameters to tune the optimization behavior, detailed in the next section.
    - /!\ make sure `ERRMOD` is settled according to the mode you want before running. This defines wether the objective displacement field is computed from a known source analytically (`0`), numerically (`1`), or from actual insar data (`2`).
- **InSAR parameters** : parameters of the InSAR tracks, such a path, look angles (heading and inclinaison, as defined in paper's Supporting Text S5), weights.
- **Executables paths** : paths towards the software needed for the execution, to modify after first installation.


### Tuning the optimization behavior

The convergence speed and the behavior of the shape optimization can be tuned acting on the following hyperparameters :
-`EPS` : precision parameter, no action on the behavior.
- `ALPHA` : Extension-regularization length, explained in Supporting information Text S2. If big compared to the mesh size, it will blur the shape, while if small it allows the development of sharper features (`HMIN`, the minimum element size must be tuned in consequence).
- `MAXIT` : usually high because the optimization is interrupted manually when a satisfying state is reached, found by checking the current stat of the shape (see next section for details).
- `MAXITLS` : maximum iteration number of the line search procedure. It allows to try different step size when the error does not decrease. Maximizing it is a good practice to make sure the step size is always optimal, but it can slow down the optimization, adding sub-iterations at each iteration.
- `TOL` : absolute amount of increase in the error allowed between two iteration. It help escaping local minimas, but may cause divergence if set too loose.
- `MULTCOEF` : value by which the step size is multiplied at each iteration, or divided during the line search if the next sub-iteration is not satisfying. Must be greater than 1. A big value (>2) drastically speeds up the convergence but can lead to very oscillatory behavior, ultimately leading to divergence, while a small value (<1.1) makes the optimization very slow.
- `MINCOEF` and `MAXCOEF` : bounds of the values for the step size, same comments than for `MULTCOEF`
- `INICOEF` : step size at the first iteration. It can be useful to lower it when the error increase immediately after iteration 0 e.g. for "hard" problems.



### Outputs and visualization

During and after the execution of the optimization (which can take a long time, from minutes to days depending on the set of parameters), it may be useful to visualize the solutions produced, especially to track an error or interrupt the loop if needed. For that, several outputs can be produced :
    - with `plot.py`, one may get similar plots to Figures 3 and 4 of the paper, as well as other visualization of the shape and trajectory. It can be executed during the optimization **in a separate console**.
    - with `anim.py`, movies of the shape evolution are computed. It can be executed during the optimization **in a separate console**.
    - with `save.py`, all the outputs and `path.py` parameters are saved in a different folder.
    - the file `u.vtu`, containing the mesh and the displacement field, updated at each iteration, can be opened in Paraview and automatically refreshed to display the current shape and its displacement field.
    - additional Paraview files or medit visualization can be generated by uncommenting the last lines of the scripts `error[N].edp`, `adjoint[N].edp`, `gradE.edp`.


## Code structure

For a more advanced usage where you wish to modify the code, you need to understand how it is structured. Overall, it is follows the same organisation of its mother code, [**sotuto**](https://github.com/dapogny/sotuto), detailed in appendix A.3 of [sotuto paper](https://dapogny.org/publis/sotuto.pdf).

Basically, `main.py` is the structure of the optimization loop, calling different functions as successive steps of each iteration. These functions are divided in two categories :
    - wrappers launching external execution of FreeFem scripts or external softwares with the correct parameters, such as the ones located in the scripts `mechtools.py` and `extools.py`
    - actual python-coded data processing or meshing functions, such as the ones from `basemesh.py` (initial meshing), `insar.py` (formatting InSAR data), `inout.py` (setting up exchange files)
Other independent scripts may be executed for specific usage, such as `plot.py`, `anim.py`, `save.py`, `benchmark.py`.

As all the information that matter is stored in exchange and mesh files stored in the `RES` folder, almost all the individual components can be run individually as soon as the folder setup is done, even if the main loop crashes. For example, a FreeFem script can be called individually from the `magmaOpt` folder if the appropriate files are already created, such as :
```bash
FreeFem++ sources/elasticity.edp
```
Depending on you needs, you may modify the FreeFem scripts directly, or the python scripts. A good way to test a modification is to run a standard synthetic test case, and as soon as it stop because of an error, run the function or script causing the error in a separate console.



## Useful links
- Companion article ([supporting information](https://agupubs.onlinelibrary.wiley.com/action/downloadSupplement?doi=10.1029%2F2025GL120764&file=2025GL120764-sup-0001-Supporting+Information+SI-S01.pdf) are also avalaible) : https://doi.org/10.1029/2025GL120764 
- Repo github page : https://github.com/Th2ooo/magmaOpt
- **sotuto** code paper : https://dapogny.org/publis/sotuto.pdf
- Tutorial on scientific computing introducing many of the concepts used in this work, by Charles Dapogny : https://dapogny.github.io/sctuto/index.html
- Tutorial on parallel computing with FreeFem++ by Pierre Jolivet  : https://joliv.et/FreeFem-tutorial/
- GMSH documentation : https://gmsh.info/doc/texinfo/gmsh.html
- MMG documentation: https://www.mmgtools.org/documentation/documentation_index.html
- Medit documentation : https://www.ljll.fr/frey/logiciels/Docmedit.dir/
- Paraview documentation : https://docs.paraview.org/en/latest/UsersGuide/index.html
