"""File providing some score functions to be used in optimization."""

import numpy as np


def MAD(tdata, data):
    """Scorefunction mean absolute difference."""
    abs_diff = np.abs(tdata - data)
    return abs_diff[~np.isnan(abs_diff)].mean()


def NormalizedMAD(tdata, data):
    """Scorefunction normalized mean absolute difference."""
    abs_diff = np.abs(tdata - data) / tdata
    return abs_diff[~np.isnan(abs_diff)].mean()
