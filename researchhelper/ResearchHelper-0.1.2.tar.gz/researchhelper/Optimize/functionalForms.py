"""Possible functional forms that can be used in system dynamics modelling."""

import numpy as np


def sigmoid(x, height=1, base=0, shift=0.5, slope=10):
    """Sigmoidal function that, using default values is bounded between [0,1] for both axes."""
    return base + (height * (1 / (1 + np.exp((-x + shift) * slope))))


def linear(x, a=1, b=0):
    """Linear function."""
    return a * x + b
