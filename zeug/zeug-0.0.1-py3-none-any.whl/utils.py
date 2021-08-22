import numpy as np


def sin_cos_transformation(a, period=None):
    a = np.array(a)

    if period is None:
        period = np.max(a)

    a_sin = np.sin((2*np.pi*a)/period)
    a_cos = np.cos((2*np.pi*a)/period)

    return a_sin, a_cos
