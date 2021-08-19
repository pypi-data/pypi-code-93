"""This module complements missing features of ``numpy.random``.

The module contains:
    * Several algorithms to sample integers without replacement.

Attribution
-----------

This code has been adapted from the scikit-learn project. Details of original source
material and how to access are provided below:

- Repository:    https://github.com/scikit-learn/scikit-learn
- Commit:        ed3642014be412b0bda13d1ec756baeabb0dcbfe
- File Path:     sklearn/model_selection/_search.py
                 sklearn/utils/_random.pyx
                 sklearn/utils/random.py
- License:       BSD 3 Clause
- Access Date:   11 July 2021
- Adapted By:    Richard Izzo (rlizzo)
- License Text:  Please refer to NOTICE file in this repository for full
                 text of original source license.
"""
import numbers
from typing import Optional, Union

import numpy as np


def _sample_without_replacement_check_input(n_population: int, n_samples: int):
    """Check that input are consistent for sample_without_replacement.
    """
    if n_population < 0:
        raise ValueError(f'n_population should be greater than 0, got {n_population}.')

    if n_samples > n_population:
        raise ValueError(
            f'n_population should be greater or equal than n_samples, got '
            f'n_samples > n_population ({n_samples} > {n_population})'
        )


def _sample_without_replacement_with_tracking_selection(n_population: int, n_samples: int, random_state=None):
    r"""Sample integers without replacement.

    Select n_samples integers from the set [0, n_population) without
    replacement.

    Time complexity:
        - Worst-case: unbounded
        - Average-case:
            O(O(np.random.randint) * \sum_{i=1}^n_samples 1 /
                                              (1 - i / n_population)))
            <= O(O(np.random.randint) *
                   n_population * ln((n_population - 2)
                                     /(n_population - 1 - n_samples)))
            <= O(O(np.random.randint) *
                 n_population * 1 / (1 - n_samples / n_population))

    Space complexity of O(n_samples) in a python set.

    Parameters
    ----------
    n_population : int
        The size of the set to sample from.

    n_samples : int
        The number of integer to sample.

    random_state : int, RandomState instance or None, default=None
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.

    Returns
    -------
    out : ndarray of shape (n_samples,)
        The sampled subsets of integer.
    """
    _sample_without_replacement_check_input(n_population, n_samples)

    out = np.empty((n_samples, ), dtype=int)  # cdef np.ndarray[np.int_t, ndim=1]

    rng = check_random_state(random_state)
    rng_randint = rng.randint

    # The following line of code are heavily inspired from python core,
    # more precisely of random.sample.
    selected = set()  # cdef set

    for i in range(n_samples):
        j = rng_randint(n_population)
        while j in selected:
            j = rng_randint(n_population)
        selected.add(j)
        out[i] = j

    return out


def _sample_without_replacement_with_pool(n_population: int, n_samples: int, random_state=None):
    """Sample integers without replacement.

    Select n_samples integers from the set [0, n_population) without
    replacement.

    Time complexity: O(n_population +  O(np.random.randint) * n_samples)

    Space complexity of O(n_population + n_samples).

    Parameters
    ----------
    n_population : int
        The size of the set to sample from.

    n_samples : int
        The number of integer to sample.

    random_state : int, RandomState instance or None, default=None
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.

    Returns
    -------
    out : ndarray of shape (n_samples,)
        The sampled subsets of integer.
    """
    _sample_without_replacement_check_input(n_population, n_samples)

    out = np.empty((n_samples, ), dtype=int)  # cdef np.ndarray[np.int_t, ndim=1]
    pool = np.empty((n_population, ), dtype=int)  # cdef np.ndarray[np.int_t, ndim=1]

    rng = check_random_state(random_state)
    rng_randint = rng.randint

    # Initialize the pool
    for i in range(n_population):
        pool[i] = i

    # The following line of code are heavily inspired from python core,
    # more precisely of random.sample.
    for i in range(n_samples):
        j = rng_randint(n_population - i)  # invariant: non-selected at [0,n-i)
        out[i] = pool[j]
        pool[j] = pool[n_population - i - 1]  # move non-selected item into vacancy

    return out


def _sample_without_replacement_with_reservoir_sampling(n_population: int, n_samples: int, random_state=None):
    """Sample integers without replacement.

    Select n_samples integers from the set [0, n_population) without
    replacement.

    Time complexity of
        O((n_population - n_samples) * O(np.random.randint) + n_samples)

    Space complexity of O(n_samples)

    Parameters
    ----------
    n_population : int
        The size of the set to sample from.

    n_samples : int
         The number of integer to sample.

    random_state : int, RandomState instance or None, default=None
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.

    Returns
    -------
    out : ndarray of shape (n_samples,)
        The sampled subsets of integer. The order of the items is not
        necessarily random. Use a random permutation of the array if the order
        of the items has to be randomized.
    """
    _sample_without_replacement_check_input(n_population, n_samples)

    out = np.empty((n_samples, ), dtype=int)  # cdef np.ndarray[np.int_t, ndim=1]

    rng = check_random_state(random_state)
    rng_randint = rng.randint

    # This cython implementation is based on the one of Robert Kern:
    # http://mail.scipy.org/pipermail/numpy-discussion/2010-December/
    # 054289.html
    #
    for i in range(n_samples):
        out[i] = i

    for i in range(n_samples, n_population):  # for i from n_samples <= i < n_population:
        j = rng_randint(0, i + 1)
        if j < n_samples:
            out[j] = i
    return out


def sample_without_replacement(n_population: int, n_samples: int, method: str = "auto", random_state=None):
    """Sample integers without replacement.

    Select n_samples integers from the set [0, n_population) without
    replacement.


    Parameters
    ----------
    n_population : int
        The size of the set to sample from.

    n_samples : int
        The number of integer to sample.

    random_state : int, RandomState instance or None, default=None
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.

    method : {"auto", "tracking_selection", "reservoir_sampling", "pool"}, \
            default='auto'
        If method == "auto", the ratio of n_samples / n_population is used
        to determine which algorithm to use:
        If ratio is between 0 and 0.01, tracking selection is used.
        If ratio is between 0.01 and 0.99, numpy.random.permutation is used.
        If ratio is greater than 0.99, reservoir sampling is used.
        The order of the selected integers is undefined. If a random order is
        desired, the selected subset should be shuffled.

        If method =="tracking_selection", a set based implementation is used
        which is suitable for `n_samples` <<< `n_population`.

        If method == "reservoir_sampling", a reservoir sampling algorithm is
        used which is suitable for high memory constraint or when
        O(`n_samples`) ~ O(`n_population`).
        The order of the selected integers is undefined. If a random order is
        desired, the selected subset should be shuffled.

        If method == "pool", a pool based algorithm is particularly fast, even
        faster than the tracking selection method. However, a vector containing
        the entire population has to be initialized.
        If n_samples ~ n_population, the reservoir sampling method is faster.

    Returns
    -------
    out : ndarray of shape (n_samples,)
        The sampled subsets of integer. The subset of selected integer might
        not be randomized, see the method argument.
    """
    _sample_without_replacement_check_input(n_population, n_samples)
    all_methods = ("auto", "tracking_selection", "reservoir_sampling", "pool")
    ratio = n_samples / n_population if n_population != 0.0 else 1.0

    # Check ratio and use permutation unless ratio < 0.01 or ratio > 0.99
    if method == "auto" and 0.01 < ratio < 0.99:
        rng = check_random_state(random_state)
        return rng.permutation(n_population)[:n_samples]

    if method == "auto" or method == "tracking_selection":
        # TODO the pool based method can also be used.
        #      however, it requires special benchmark to take into account
        #      the memory requirement of the array vs the set.
        # The value 0.2 has been determined through benchmarking.
        if ratio < 0.2:
            return _sample_without_replacement_with_tracking_selection(n_population, n_samples, random_state)
        else:
            return _sample_without_replacement_with_reservoir_sampling(n_population, n_samples, random_state)
    elif method == "reservoir_sampling":
        return _sample_without_replacement_with_reservoir_sampling(n_population, n_samples, random_state)
    elif method == "pool":
        return _sample_without_replacement_with_pool(n_population, n_samples, random_state)
    else:
        raise ValueError(f'Expected a method name in {all_methods}, got {method}.')


def check_random_state(seed: Optional[Union['numbers.Integral', 'np.random.RandomState']]):
    """Turn seed into a np.random.RandomState instance

    Parameters
    ----------
    seed :
        If seed is None, return the RandomState singleton used by np.random.
        If seed is an int, return a new RandomState instance seeded with seed.
        If seed is already a RandomState instance, return it.
        Otherwise raise ValueError.
    """
    if seed is None or seed is np.random:
        return np.random.mtrand._rand
    if isinstance(seed, numbers.Integral):
        return np.random.RandomState(seed)
    if isinstance(seed, np.random.RandomState):
        return seed
    raise ValueError(f"{seed} cannot be used to seed a numpy.random.RandomState instance")
