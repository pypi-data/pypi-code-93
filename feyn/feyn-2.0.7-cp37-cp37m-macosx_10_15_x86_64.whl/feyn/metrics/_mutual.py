"""
Code for calculating the mutual information (MI)
between several random variables.
"""

import numpy as np
from functools import reduce

from typing import Iterable, Union, Tuple

def calculate_mi(rv_samples:Iterable[Iterable], float_bins:int=None) -> float:
    """
    Numpy-based implementation of mutual information for n random variables.
    This can be used for both categorical (discrete) and continuous variables,
    you can as many as you want of each, in any position in the iterable.

    Arguments:
        rv_samples {Iterable[Iterable]} -- Samples from random variables given inside an iterable.
        In the traditional ML sense, these would be the data of the input features.

    Keyword Arguments:
        float_bins {Union[Tuple[int], int]} -- Number of bins in which to count numerical random variables.
        If None is given, numerical variables are divided in equally spaced bins given by max{min{n_samples/3, 10}, 2}.

    Returns:
        float -- The mutual information between the input random variables.
    """

    if float_bins is None:
        float_bins = _float_discretization(len(rv_samples[0]))

    # Construct samples and bins
    bins = []
    rv_input = []

    for rv in rv_samples:
        if type(rv).__name__ == "Series":
            sample = rv.iloc[0]
        else:
            sample = rv[0]

        if isinstance(sample, float) and sample != sample.astype(int):
            bins.append(float_bins)
            rv_input.append(rv)
        else:
            if isinstance(sample, (np.integer, int, float, np.float_)):
                bins.append(len(np.unique(rv))+1)
                rv_input.append(rv)
            else:
                rv_encoded, ncats = _encode(rv)
                rv_input.append(rv_encoded)
                bins.append(ncats)

    joint_dist = _normalize_hist(np.histogramdd(rv_input, bins=bins)[0])

    marginals = [_integrate_to(joint_dist, i) for i in range(joint_dist.ndim)]
    outer_dist = _normalize_hist(_nd_outer(*marginals))

    nz_idx = np.nonzero(joint_dist)
    nz_joint = joint_dist[nz_idx]
    nz_outer = outer_dist[nz_idx]

    return np.sum(nz_joint * (np.log(nz_joint) - np.log(nz_outer)))

def _float_discretization(n_samples):
    """
    Calculate the discretization of continuous features by cutting the range of values in q equally spaced intervals,
    where q = max{min{n_samples / 3, 10}, 2}.
    """
    return int(np.maximum(np.minimum(n_samples / 3, 10), 2))

def _nd_outer(*vecs):
    """
    Calculate the outer product of n vectors, given as positional arguments. Return an n-dimensional array as a result.
    """
    return reduce(np.multiply.outer, vecs)

def _integrate_to(arr, axis):
    """
    Given an n-dim array arr and an axis, sum all other axes to that one.
    """
    all_axes = range(arr.ndim)
    sum_these = tuple(ax for ax in all_axes if ax != axis)
    return arr.sum(axis=sum_these)

def _normalize_hist(arr):
    """
    Given an n-d array arr that represents a histogram, move from talking about counts to talking about probabilities (not probability densities).
    """
    return arr / arr.sum()

def _encode(discrete_rv):
    """
    Encode a 1D discrete random variable that does not contain integers to one that does.
    """
    ret = discrete_rv.copy()
    elems = np.unique(discrete_rv)

    for int_label, elem in enumerate(elems):
        ret[discrete_rv == elem] = int_label

    return ret.astype(int), len(elems)
