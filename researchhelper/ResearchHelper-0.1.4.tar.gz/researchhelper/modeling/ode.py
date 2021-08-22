"""Simulation bases."""

from scipy.integrate import odeint
import numpy as np


def ODESimulation(ODE, timesteps, resolution, y0, a, f):
    """Set up an ODE simulation.

    Parameters
    ----------
    ODE : Function
        Your function describing the set of ordinary differential equations.
    timesteps : int
        The number of steps you want to simulate.
    resolution : int
        How many datapoints do you want per time step?
    y0 : Tuple
        A tuple of your initial conditions.
    a : Tuple
        A tuple of your variables that you'd eventually want to fit.
    f : Tuple
        A tuple containing the functions you'd want to fit.

    Returns
    -------
    time : Array
        x-axis time data
    data : numpy.ndarray
        Numpy array of your output

    """
    # Set up time
    time = np.linspace(1, timesteps, timesteps * resolution)

    # Get data
    data = odeint(ODE, y0, time, args=(a, f))

    return time, data
