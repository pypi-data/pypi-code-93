import numpy as np


def sin_cos_transformation(a, period=None):
    a = np.array(a)

    if period is None:
        period = np.max(a)

    a_sin = np.sin((2*np.pi*a)/period)
    a_cos = np.cos((2*np.pi*a)/period)

    return a_sin, a_cos


def synth_ts(n=100, base=100, r_down=0.05, r_up=0.05):
    ts = np.array([])

    for t in range(n):
        r = np.random.uniform(low=1-r_down, high=1+r_up)
        base = base*r
        ts = np.append(ts, base)

    return ts
