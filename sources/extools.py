#!/usr/bin/pythonw
# -*-coding:Utf-8 -*

import subprocess
import sources.path as path

""" 
Wrappers functions to call external programs for
    -advection : advect
    -level set computation :  mshdist
    -level set remeshing : mmg3d
"""



def advect(mesh, phi, vel, step, newphi):
    """
    Advect the L.S. function in ssol via the velocity svel; result in ssolout
    Parameters
    ----------
    mesh : str
        input mesh file
    phi : str
        input LS file.
    vel : str
        input velocity field.
    step : float
        step size.
    newphi : str
        output level set file.
    """
    log = open(path.LOGFILE, 'a')

    # Advection by calling advect
    proc = subprocess.Popen(["{adv} {msh} -s {vit} -c {chi} -dt {dt} -o {out} -nocfl".format(
        adv=path.ADVECT, msh=mesh, vit=vel, chi=phi, dt=step, out=newphi)], shell=True, stdout=log)
    proc.wait()

    log.close()



def mshdist(mesh, phi):
    """
    Create the signed distance function to the subdomain labelled path.REFINT  

    Parameters
    ----------
    mesh : str
        path name of the mesh.
    phi : str
        path name of the output distance field.
    """

    log = open(path.LOGFILE, 'a')

    # Distancing with mshdist
    proc = subprocess.Popen(
        ["{mshdist} {msh} -dom -fmm".format(mshdist=path.MSHDIST, msh=mesh)], shell=True, stdout=log)
    proc.wait()

    # Move output file to the desired location
    oldphi = mesh.replace('.mesh', '') + ".sol"
    proc = subprocess.Popen(["mv {old} {new}".format(
        old=oldphi, new=phi)], shell=True, stdout=log)
    proc.wait()

    log.close()




def mmg3d(mesh, ls, phi, hmin, hmax, hausd, hgrad, nr, out):
    """
    Call to mmg3d fro remeshng or to mesh a level set function as a new boundary 
    in an existing mesh

    Parameters
    ----------
    mesh : str
        name of the mesh.
    ls : int
        0 for standard remeshing mode, 1 for L.S. discretization mode        
    phi : str
        path name of the L.S. function.
    hmin : real
        minimum desired size of an element in the mesh.
    hmax : real
        maximum desired size of an element in the mesh.
    hausd : real
        geometric approximation parameter.
    hgrad : real
        mesh gradation parameter.
    nr : int
        0 if identification of sharp angles, 1 if no identification .
    out : str
        path name of the output mesh  .


    Returns
    -------
    int
        1 if remeshing successful, 0 otherwise.

    """

    log = open(path.LOGFILE, 'a')

    if ls:
        if nr:
            # print("nr+ls in remeshing")
            # !!!! option -optim added to avoid modyfing mesh size but may cause problems
            proc = subprocess.Popen(["{mmg} {mesh} -ls -sol {sol} -hmin {hmin} -hmax {hmax} -hausd {hausd} -hgrad {hgrad} -nr {res} -rmc".format(
                mmg=path.MMG3D, mesh=mesh, sol=phi, hmin=hmin, hmax=hmax, hausd=hausd, hgrad=hgrad, res=out)], shell=True, stdout=log)

            proc.wait()
        else:
            proc = subprocess.Popen(["{mmg} {mesh} -ls -sol {sol} -hmin {hmin} -hmax {hmax} -hausd {hausd} -hgrad {hgrad} {res} -rmc".format(
                mmg=path.MMG3D, mesh=mesh, sol=phi, hmin=hmin, hmax=hmax, hausd=hausd, hgrad=hgrad, res=out)], shell=True, stdout=log)
            proc.wait()
    else:
        if nr:
            proc = subprocess.Popen(["{mmg} {mesh} -hmin {hmin} -hmax {hmax} -hausd {hausd} -hgrad {hgrad} -nr {res} -rmc".format(
                mmg=path.MMG3D, mesh=mesh, sol=phi, hmin=hmin, hmax=hmax, hausd=hausd, hgrad=hgrad, res=out)], shell=True, stdout=log)
            proc.wait()
        else:
            proc = subprocess.Popen(["{mmg} {mesh} -hmin {hmin} -hmax {hmax} -hausd {hausd} -hgrad {hgrad} {res} -rmc".format(
                mmg=path.MMG3D, mesh=mesh, sol=phi, hmin=hmin, hmax=hmax, hausd=hausd, hgrad=hgrad, res=out)], shell=True, stdout=log)
            proc.wait()

    log.close()
    if (proc.returncode != 0):
        raise Exception("MMG remeshing failed !")
    else:
        return 1

