# -*- coding: utf-8 -*-
"""
Functions related to optimisation with casadi.

This file can also be imported as a module and contains the following
functions:


References:
    [1] J.B. Petersen, casadi_intro, https://github.com/borlum/casadi_intro 

"""

# Import all useful libraries
import casadi as ca
import casadi.tools
import numpy as np


# Propagation method
def runge_kuta(f, x, u, v, dt, order=4):
    """Operates algorithmic differentiation according to the Runge-Kuta method.

    The state space model description used is:

    dx/dt = f(x,u,v)

    Parameters
    ----------
    f : function
        f(x,u,v)
    x : casadi.tools.struct_symMX
        State vector
    u : casadi.tools.struct_symMX
        Input vector
    v : casadi.tools.struct_symMX
        Disturbance vector

    dt : casadi.MX.sym
        Time step

    order : int
        Order of the Runge-Kuta method
        Default: 4

    Raises
    ------
    None

    Returns
    -------
    F_SSM : casadi.Function
        Single step propagation function
    """
    if order == 4:
        # Adapting implementation from [1] for RK4
        k1 = f(x, u, v)
        k2 = f(x + dt / 2.0 * k1, u, v)
        k3 = f(x + dt / 2.0 * k2, u, v)
        k4 = f(x + dt * k3, u, v)
        xf = x + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)

        # Single step time propagation
        F_SSM = ca.Function(
            "F_SSM", [x, u, v, dt], [xf], ["x[k]", "u[k]", "v[k]", "dt"], ["x[k+1]"]
        )

    else:
        raise Exception("This order is not supported yet ({})".format(order))

    return F_SSM


def solve_optimisation(problem, solver="ipopt", verbose=False, **kwargs):
    """Solves an optimisation problem with Casadi

    Parameters
    ----------
    problem : casadi.Opti
        Problem to solve

    solver : str
        Solver to use
        Default : "ipopt"
        State vector

    verbose : Boolean
        Provide log outputs if True
        Default : False

    Raises
    ------
    None

    Returns
    -------
    sol : casadi.(solution)
        Solution of the optimisation
    """
    if solver == "ipopt":
        solver2use = solver
        if verbose is True:
            settings = {"ipopt": {"print_level": 1}}
        else:
            settings = {"ipopt": {"print_level": 0}}
    else:
        raise Exception("Illegal solver ({})".format(solver))

    problem.solver(solver2use, settings)
    sol = problem.solve()
    return sol


def extract_optimisation_results(solution, model, data, X, U, V, keep=[]):
    """Solves an optimisation problem with Casadi

    Parameters
    ----------
    solution : casadi.(solution)
        Problem to solve

    model : str
        Solver to use
        Default : "ipopt"
        State vector

    data : pandas.DataFrame
        Data providing the skeleton of the output timeseries

    X,U,V : pandas.DataFrame
        State, input and output data

    keep : list(str)
        Names of the columns of input "data" to keep
        Default : []

    Raises
    ------
    None

    Returns
    -------
    timeseries : pandas.DataFrame
        Dataframe with inputs and outputs of optimisation
    """
    F_SSM = model["SSM"]
    fields_u = model["data_fields"]["u"]
    fields_v = model["data_fields"]["v"]
    fields_x = model["data_fields"]["x"]

    # Structuring the outputs
    timeseries = data[keep].copy()

    for i in range(len(fields_x)):
        fx_i = fields_x[i]
        timeseries[fx_i] = np.nan
        timeseries[fx_i] = solution.value(X[i, :])[0:-1]

    for i in range(len(fields_u)):
        fu_i = fields_u[i]
        timeseries[fu_i] = np.nan
        timeseries[fu_i] = solution.value(U[i, :])

    for i in range(len(fields_v)):
        fv_i = fields_v[i]
        timeseries[fv_i] = np.nan
        timeseries[fv_i] = solution.value(V[i, :])

    return timeseries
