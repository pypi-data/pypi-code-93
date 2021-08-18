"""This module includes methods to fine-tune the parameters of a sweep.

The grid search provided by GridSearchCV exhaustively generates candidates
from a grid of parameter values specified with the param_grid parameter.
For instance, the following param_grid:

param_grid = [
  {'C': [1, 10, 100, 1000], 'kernel': ['linear']},
  {'C': [1, 10, 100, 1000], 'gamma': [0.001, 0.0001], 'kernel': ['rbf']},
 ]

specifies that two grids should be explored: one with a linear kernel and C
values in [1, 10, 100, 1000], and the second one with an RBF kernel, and the
cross-product of C values ranging in [1, 10, 100, 1000] and gamma values
in [0.001, 0.0001].

Attribution
-----------

This code has been adapted from the scikit-learn project. Details of original source
material and how to access are provided below:

- Repository:    https://github.com/scikit-learn/scikit-learn
- Commit:        ed3642014be412b0bda13d1ec756baeabb0dcbfe
- File Path:     sklearn/model_selection/_search.py
- License:       BSD 3 Clause
- Access Date:   11 July 2021
- Adapted By:    Richard Izzo (rlizzo)
- License Text:  Please refer to NOTICE file in this repository for full
                 text of original source license.
"""
from functools import partial, reduce
from itertools import product
import operator
from typing import Any, Iterable, Mapping, Optional, Sequence, Union
import warnings

import numpy as np

from grid.sdk.sweeps.sampling import check_random_state, sample_without_replacement


class ParameterGrid:
    """Grid of parameters with a discrete number of values for each.

    Can be used to iterate over parameter value combinations with the
    Python built-in function iter.

    The order of the generated parameter combinations is deterministic.
    Read more in the :ref:`User Guide <grid_search>`.

    Parameters
    ----------
    param_grid
        The parameter grid to explore, as a dictionary mapping estimator
        parameters to sequences of allowed values.

        An empty dict signifies default parameters.

        A sequence of dicts signifies a sequence of grids to search, and is
        useful to avoid exploring parameter combinations that make no sense
        or have no effect. See the examples below.

    Examples
    --------
    >>> from grid.sdk.sweeps.grid_search_strategy import ParameterGrid
    >>> param_grid = {'a': [1, 2], 'b': [True, False]}
    >>> list(ParameterGrid(param_grid)) == (
    ...    [{'a': 1, 'b': True}, {'a': 1, 'b': False},
    ...     {'a': 2, 'b': True}, {'a': 2, 'b': False}])
    True
    >>> grid = [{'kernel': ['linear']}, {'kernel': ['rbf'], 'gamma': [1, 10]}]
    >>> list(ParameterGrid(grid)) == [{'kernel': 'linear'},
    ...                               {'kernel': 'rbf', 'gamma': 1},
    ...                               {'kernel': 'rbf', 'gamma': 10}]
    True
    >>> ParameterGrid(grid)[1] == {'kernel': 'rbf', 'gamma': 1}
    True

    See Also
    --------
    GridSearchCV : Uses :class:`ParameterGrid` to perform a full parallelized
        parameter search.
    """
    def __init__(self, param_grid: Union[Mapping[str, Sequence], Sequence[Mapping[str, Sequence]]]):
        if not isinstance(param_grid, (Mapping, Iterable)):
            raise TypeError("Parameter grid is not a dict or a list ({!r})".format(param_grid))

        if isinstance(param_grid, Mapping):
            # wrap dictionary in a singleton list to support either dict
            # or list of dicts
            param_grid = [param_grid]

        # check if all entries are dictionaries of lists
        for grid in param_grid:
            if not isinstance(grid, dict):
                raise TypeError("Parameter grid is not a dict ({!r})".format(grid))
            for key in grid:
                if not isinstance(grid[key], Iterable):
                    raise TypeError(
                        "Parameter grid value is not iterable "
                        "(key={!r}, value={!r})".format(key, grid[key])
                    )

        self.param_grid = param_grid

    def __iter__(self):
        """Iterate over the points in the grid.
        Returns
        -------
        params : iterator over dict of str to any
            Yields dictionaries mapping each estimator parameter to one of its
            allowed values.
        """
        for p in self.param_grid:
            # Always sort the keys of a dictionary, for reproducibility
            items = sorted(p.items())
            if not items:
                yield {}
            else:
                keys, values = zip(*items)
                for v in product(*values):
                    params = dict(zip(keys, v))
                    yield params

    def __len__(self):
        """Number of points on the grid."""
        # Product function that can handle iterables (np.product can't).
        _product = partial(reduce, operator.mul)
        return sum(_product(len(v) for v in p.values()) if p else 1 for p in self.param_grid)

    def __getitem__(self, ind: int):
        """Get the parameters that would be ``ind``th in iteration
        Parameters
        ----------
        ind
            The iteration index
        Returns
        -------
        params : dict of str to any
            Equal to list(self)[ind]
        """
        # This is used to make discrete sampling without replacement memory
        # efficient.
        for sub_grid in self.param_grid:
            # XXX: could memoize information used here
            if not sub_grid:
                if ind == 0:
                    return {}
                ind -= 1
                continue

            # Reverse so most frequent cycling parameter comes first
            keys, values_lists = zip(*sorted(sub_grid.items())[::-1])
            sizes = [len(v_list) for v_list in values_lists]
            total = np.product(sizes)

            if ind >= total:
                # Try the next grid
                ind -= total
            else:
                out = {}
                for key, v_list, n in zip(keys, values_lists, sizes):
                    ind, offset = divmod(ind, n)
                    out[key] = v_list[offset]
                return out

        raise IndexError("ParameterGrid index out of range")


class ParameterSampler:
    """Generator on parameters sampled from given distributions.

    Non-deterministic iterable over random candidate combinations for
    hyper-parameter search. If all parameters are presented as a list,
    sampling without replacement is performed. If at least one parameter
    is given as a distribution, sampling with replacement is used. It
    is highly recommended to use continuous distributions for continuous
    parameters.

    Read more in the :ref:`User Guide <grid_search>`.

    Parameters
    ----------
    param_distributions
        Dictionary with parameters names (`str`) as keys and distributions
        or lists of parameters to try. Distributions must provide a ``rvs``
        method for sampling (such as those from scipy.stats.distributions).

        If a list is given, it is sampled uniformly.

        If a list of dicts is given, first a dict is sampled uniformly, and
        then a parameter is sampled using that dict as above.

    n_iter : int
        Number of parameter settings that are produced.

    random_state : int, RandomState instance or None, default=None
        Pseudo random number generator state used for random uniform sampling
        from lists of possible values instead of scipy.stats distributions.

        Pass an int for reproducible output across multiple function calls.

    Returns
    -------
    params : dict of str to any
        **Yields** dictionaries mapping each estimator parameter to as sampled value.

    Examples
    --------
    >>> from grid.sdk.sweeps.grid_search_strategy import ParameterSampler
    >>> import numpy as np
    >>> import scipy.stats
    >>> rng = np.random.RandomState(0)
    >>> param_grid = {'a':[1, 2], 'b': scipy.stats.expon(scale=1.0)}
    >>> param_list = list(ParameterSampler(param_grid, n_iter=4, random_state=rng))
    >>> rounded_list = [dict((k, round(v, 6)) for (k, v) in d.items())
    ...                 for d in param_list]
    >>> rounded_list == [{'b': 0.89856, 'a': 1},
    ...                  {'b': 0.923223, 'a': 1},
    ...                  {'b': 1.878964, 'a': 2},
    ...                  {'b': 1.038159, 'a': 2}]
    True
    """
    def __init__(
        self,
        param_distributions: Union[Union[Mapping[str, Any], Sequence[Union[str, Any]]], Sequence[Any],
                                   Sequence[Mapping[str, Any]]],
        n_iter: int,
        *,
        random_state: Optional[Union[np.random.RandomState, int]] = None
    ):
        if not isinstance(param_distributions, (Mapping, Iterable)):
            raise TypeError("Parameter distribution is not a dict or a list ({!r})".format(param_distributions))

        if isinstance(param_distributions, Mapping):
            # wrap dictionary in a singleton list to support either dict
            # or list of dicts
            param_distributions = [param_distributions]

        for dist in param_distributions:
            if not isinstance(dist, dict):
                raise TypeError("Parameter distribution is not a dict ({!r})".format(dist))
            for key in dist:
                if not isinstance(dist[key], Iterable) and not hasattr(dist[key], "rvs"):
                    raise TypeError(
                        "Parameter value is not iterable "
                        "or distribution (key={!r}, value={!r})".format(key, dist[key])
                    )
        self.n_iter = n_iter
        self.random_state = random_state
        self.param_distributions = param_distributions

    def _is_all_lists(self):
        return all(all(not hasattr(v, "rvs") for v in dist.values()) for dist in self.param_distributions)

    def __iter__(self):
        rng = check_random_state(self.random_state)

        # if all distributions are given as lists, we want to sample without
        # replacement
        if self._is_all_lists():
            # look up sampled parameter settings in parameter grid
            param_grid = ParameterGrid(self.param_distributions)
            grid_size = len(param_grid)
            n_iter = self.n_iter

            if grid_size < n_iter:
                warnings.warn(
                    "The total space of parameters %d is smaller "
                    "than n_iter=%d. Running %d iterations. For exhaustive "
                    "searches, use GridSearchCV." % (grid_size, self.n_iter, grid_size),
                    UserWarning,
                )
                n_iter = grid_size
            for i in sample_without_replacement(grid_size, n_iter, random_state=rng):
                yield param_grid[i]

        else:
            for _ in range(self.n_iter):
                dist = rng.choice(self.param_distributions)
                # Always sort the keys of a dictionary, for reproducibility
                items = sorted(dist.items())
                params = {}
                for k, v in items:
                    if hasattr(v, "rvs"):
                        params[k] = v.rvs(random_state=rng)
                    else:
                        params[k] = v[rng.randint(len(v))]
                yield params

    def __len__(self):
        """Number of points that will be sampled."""
        if self._is_all_lists():
            grid_size = len(ParameterGrid(self.param_distributions))
            return min(self.n_iter, grid_size)
        return self.n_iter


def _check_param_grid(param_grid):
    if hasattr(param_grid, "items"):
        param_grid = [param_grid]

    for p in param_grid:
        for name, v in p.items():
            if isinstance(v, np.ndarray) and v.ndim > 1:
                raise ValueError("Parameter array should be one-dimensional.")

            if isinstance(v, str) or not isinstance(v, (np.ndarray, Sequence)):
                raise ValueError(
                    "Parameter grid for parameter ({0}) needs to"
                    " be a list or numpy array, but got ({1})."
                    " Single values need to be wrapped in a list"
                    " with one element.".format(name, type(v))
                )

            if len(v) == 0:
                raise ValueError(
                    "Parameter values for parameter ({0}) need "
                    "to be a non-empty sequence.".format(name)
                )
