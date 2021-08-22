"""Possible functional forms that can be used in system dynamics modelling."""

import numpy as np


def sigmoid(x, height=1, base=0, shift=0.5, slope=10):
    """Sigmoidal function that, using default values is bounded between [0,1] for both axes.

    Parameters
    ----------
    x : int
        Input for function.
    height : float
        Controls the height of the sigmoid. (Default value = 1).
    base : float
        Controls the lowest point of the sigmoid. (Default value = 0)
    shift : float
        Controls the shifting of the sigmoid (to left or right), the midpoint
        will end up here. (Default value = 0.5)
    slope : float
        Controls the steepness or slope of the sigmoid. (Default value = 10)

    Returns
    -------
    value : float
        Calculated y-coordinate of sigmoid.

    """
    return base + (height * (1 / (1 + np.exp((-x + shift) * slope))))


def linear(x, a=1, b=0):
    """Linear function.

    Parameters
    ----------
    x : float
        Input for function.
    a : float
        Slope of the line. (Default value = 1)
    b : float
        The y-intercept. (Default value = 0)

    Returns
    -------
    value : float
        Calculated y-coordinate of linear function.
    """
    return a * x + b
