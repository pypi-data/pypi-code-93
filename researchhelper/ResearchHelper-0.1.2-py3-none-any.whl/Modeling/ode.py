"""Simulation bases."""

from scipy.integrate import odeint
import numpy as np


def ODESimulation(ODE, timesteps, resolution, y0, a, f):
    """Set up an ODE simulation."""
    # Set up time
    time = np.linspace(1, timesteps, timesteps * resolution)

    # Get data
    data = odeint(ODE, y0, time, args=(a, f))

    return time, data
