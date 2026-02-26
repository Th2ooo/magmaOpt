#!/usr/bin/pythonw
# -*-coding:Utf-8 -*

import subprocess
import sources.path as path
import sources.inout as inout

"""
Wrappers to call all the FreeFem++ scripts corrsponding to the different FEM resolution
needed during the optimization process

TODO: on some functions remove useless parameters
"""


def elasticity(mesh, u):
    """
    Solve elasticity problem on mesh file and store in in u file
    
    Parameters
    ----------
    mesh : str
        path of the mesh for D.
    u : str
        path of the output displacement field.
    """
    
    # Set information in exchange file
    inout.setAtt(file=path.EXCHFILE, attname="MeshName", attval=mesh)
    inout.setAtt(file=path.EXCHFILE, attname="DispName", attval=u)

    # Call to FreeFem
    log = open(path.LOGFILE, 'a')

    proc = subprocess.Popen(["{FreeFem} {elasticity} > /dev/null 2>&1".format(
        FreeFem=path.FREEFEM, elasticity=path.FFELAS)], shell=True, stdout=log)
    proc.wait()

    log.close()

    return proc

    if (proc.returncode != 0):
        print("Error in numerical solver; abort. OOO")
        print(proc.returncode)




def adjoint(mesh, u, p):
    """
    Computation of the adjoint state for the ERROR functional. The adjoint script
    called depend on the path.ERRMOD

    Parameters
    ----------
    mesh : str
        mesh name of the domain D.
    u : str
        input elastic displacement field.
    p : str
        path of the output adjoint state.

    """

    # Set information in exchange file
    inout.setAtt(file=path.EXCHFILE, attname="MeshName", attval=mesh)
    inout.setAtt(file=path.EXCHFILE, attname="DispName", attval=u)
    inout.setAtt(file=path.EXCHFILE, attname="AdjName", attval=p)

    # Call to FreeFem
    proc = subprocess.Popen(["{FreeFem} {adjoint} > /dev/null 2>&1".format(
        FreeFem=path.FREEFEM, adjoint=path.FFADJ)], shell=True)
    proc.wait()

    if (proc.returncode != 0):
        print(proc.returncode)
        raise Exception(
            "Error in numerical solver for adjoint equation; abort.")



def error(mesh, u):
    """
    Calculate error functional data-model JLS(Omega)

    Parameters
    ----------
    mesh : str
        path of mesh of the full domain D.
    u : str
        path of the input displacement field.

    Raises
    ------
    Exception
        DESCRIPTION.

    Returns
    -------
    err : real
        The value of JLS for the given shape 

    """

    # Set information in exchange file
    inout.setAtt(file=path.EXCHFILE, attname="MeshName", attval=mesh)
    inout.setAtt(file=path.EXCHFILE, attname="DispName", attval=u)

    # Call to FreeFem
    proc = subprocess.Popen(["{FreeFem} {error} > /dev/null 2>&1".format(
        FreeFem=path.FREEFEM, error=path.FFERR)], shell=True)
    proc.wait()

    if (proc.returncode != 0):
        print(proc.returncode)
        raise Exception("Error in error calculation; abort.")

    [err] = inout.getrAtt(file=path.EXCHFILE, attname="Error")
    [resi] = inout.getrAtt(file=path.EXCHFILE, attname="ResMag")

    return err, resi


def stats(mesh):
    """
    Compute quantities on the shape Omega

    Parameters
    ----------
    mesh : str
        path of the mesh of D.

    Returns
    -------
    vol : real
        total volume of the shape.
    barx : real
        x coordinate of the barycenter.
    bary : real
        y coordinate of the barycenter.
    barz : real
        z coordinate of the barycenter.

    """

    # Set information in exchange file
    inout.setAtt(file=path.EXCHFILE, attname="MeshName", attval=mesh)

    # Call to FreeFem
    proc = subprocess.Popen(["{FreeFem} {stats} > /dev/null 2>&1".format(
        FreeFem=path.FREEFEM, stats=path.FFSTATS)], shell=True)
    proc.wait()

    if (proc.returncode != 0):
        print("Error in stats calculation; abort.")
        raise Exception(
            "Error in calculung geometrical statisitics (no source ?)")
        print(proc.returncode)

    [vol] = inout.getrAtt(file=path.EXCHFILE, attname="Volume")
    [barx] = inout.getrAtt(file=path.EXCHFILE, attname="Barx")
    [bary] = inout.getrAtt(file=path.EXCHFILE, attname="Bary")
    [barz] = inout.getrAtt(file=path.EXCHFILE, attname="Barz")

    return vol, barx, bary, barz



def gradE(mesh, disp, adj, grad, phi):
    """
    Calculate gradient of the ERROR functional
    
    Parameters
    ----------
    mesh : str
        mesh of D.
    disp : str
        path of the elastic displacement field.
    adj : str
        path of the adjoint field.
    grad : str
        path where to output the gradient.
    phi : str
        path of the LS field.

    """
    # Set information in exchange file
    inout.setAtt(file=path.EXCHFILE, attname="MeshName", attval=mesh)
    inout.setAtt(file=path.EXCHFILE, attname="DispName", attval=disp)
    inout.setAtt(file=path.EXCHFILE, attname="AdjName", attval=adj)
    inout.setAtt(file=path.EXCHFILE, attname="GradEName", attval=grad)
    inout.setAtt(file=path.EXCHFILE, attname="PhiName", attval=phi)

    # Call to FreeFem
    proc = subprocess.Popen(["{FreeFem} {gradE} > /dev/null 2>&1".format(
        FreeFem=path.FREEFEM, gradE=path.FFGRADE)], shell=True)
    proc.wait()

    if (proc.returncode != 0):
        print("Error in calculation of gradient of ERROR; abort.")
        print(proc.returncode)


def descent(mesh, phi, E, gE, g):
    """
    Calculation of the (normalized) descent direction

    Parameters
    ----------
    mesh : str
        mesh of D.
    phi : str
        path of the LS field.
    E : real
        current error.
    gE : str
        path of the gradient .
    g : str
        path where to output the descent field.
    """

    inout.setAtt(file=path.EXCHFILE, attname="MeshName", attval=mesh)
    inout.setAtt(file=path.EXCHFILE, attname="PhiName", attval=phi)
    inout.setAtt(file=path.EXCHFILE, attname="GradEName", attval=gE)
    inout.setAtt(file=path.EXCHFILE, attname="Error", attval=E)
    inout.setAtt(file=path.EXCHFILE, attname="GradName", attval=g)

    # Velocity extension - regularization via FreeFem
    proc = subprocess.Popen(["{FreeFem} {ffdescent} > /dev/null 2>&1".format(
        FreeFem=path.FREEFEM, ffdescent=path.FFDESCENT)], shell=True)
    proc.wait()

    if (proc.returncode != 0):
        print(proc.returncode)
        raise Exception("Error in calculation of descent direction; abort.")

