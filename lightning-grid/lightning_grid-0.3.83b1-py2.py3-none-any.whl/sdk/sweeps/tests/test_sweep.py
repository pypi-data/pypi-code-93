"""Test the hyperparameters module.

Attribution
-----------

This code has been adapted from the scikit-learn project. Details of original source
material and how to access are provided below:

- Repository:    https://github.com/scikit-learn/scikit-learn
- Commit:        ed3642014be412b0bda13d1ec756baeabb0dcbfe
- File Path:     sklearn/model_selection/tests/test_search.py
- License:       BSD 3 Clause
- Access Date:   11 July 2021
- Adapted By:    Richard Izzo (rlizzo)
- License Text:  Please refer to NOTICE file in this repository for full
                 text of original source license.
"""
from collections.abc import Iterable, Sized
from functools import partial
from itertools import chain, product

import pytest

scipy_stats = pytest.importorskip("scipy.stats")

from grid.sdk.sweeps.grid_search_strategy import ParameterGrid, ParameterSampler


def assert_grid_iter_equals_getitem(grid):
    assert list(grid) == [grid[i] for i in range(len(grid))]


@pytest.mark.parametrize("klass", [ParameterGrid, partial(ParameterSampler, n_iter=10)])
@pytest.mark.parametrize(
    "input, error_type, error_message",
    [
        (0, TypeError, r"Parameter .* is not a dict or a list \(0\)"),
        ([{
            "foo": [0]
        }, 0], TypeError, r"Parameter .* is not a dict \(0\)"),
        (
            {
                "foo": 0
            },
            TypeError,
            "Parameter.* value is not iterable .*"
            r"\(key='foo', value=0\)",
        ),
    ],
)
def test_validate_parameter_input(klass, input, error_type, error_message):
    with pytest.raises(error_type, match=error_message):
        klass(input)


def test_parameter_grid():

    # Test basic properties of ParameterGrid.
    params1 = {"foo": [1, 2, 3]}
    grid1 = ParameterGrid(params1)
    assert isinstance(grid1, Iterable)
    assert isinstance(grid1, Sized)
    assert len(grid1) == 3
    assert_grid_iter_equals_getitem(grid1)

    params2 = {"foo": [4, 2], "bar": ["ham", "spam", "eggs"]}
    grid2 = ParameterGrid(params2)
    assert len(grid2) == 6

    # loop to assert we can iterate over the grid multiple times
    for i in range(2):
        # tuple + chain transforms {"a": 1, "b": 2} to ("a", 1, "b", 2)
        points = set(tuple(chain(*(sorted(p.items())))) for p in grid2)
        assert points == set(("bar", x, "foo", y) for x, y in product(params2["bar"], params2["foo"]))
    assert_grid_iter_equals_getitem(grid2)

    # Special case: empty grid (useful to get default estimator settings)
    empty = ParameterGrid({})
    assert len(empty) == 1
    assert list(empty) == [{}]
    assert_grid_iter_equals_getitem(empty)
    with pytest.raises(IndexError):
        _ = empty[1]

    has_empty = ParameterGrid([{"C": [1, 10]}, {}, {"C": [0.5]}])
    assert len(has_empty) == 4
    assert list(has_empty) == [{"C": 1}, {"C": 10}, {}, {"C": 0.5}]
    assert_grid_iter_equals_getitem(has_empty)


def test_param_sampler():
    # test basic properties of param sampler
    param_distributions = {"kernel": ["rbf", "linear"], "C": scipy_stats.uniform(0, 1)}
    sampler = ParameterSampler(param_distributions=param_distributions, n_iter=10, random_state=0)
    samples = [x for x in sampler]
    assert len(samples) == 10
    for sample in samples:
        assert sample["kernel"] in ["rbf", "linear"]
        assert 0 <= sample["C"] <= 1

    # test that repeated calls yield identical parameters
    param_distributions = {"C": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
    sampler = ParameterSampler(param_distributions=param_distributions, n_iter=3, random_state=0)
    assert [x for x in sampler] == [x for x in sampler]

    param_distributions = {"C": scipy_stats.uniform(0, 1)}
    sampler = ParameterSampler(param_distributions=param_distributions, n_iter=10, random_state=0)
    assert [x for x in sampler] == [x for x in sampler]


def test_parameters_sampler_replacement():
    # raise warning if n_iter is bigger than total parameter space
    params = [
        {
            "first": [0, 1],
            "second": ["a", "b", "c"]
        },
        {
            "third": ["two", "values"]
        },
    ]
    sampler = ParameterSampler(params, n_iter=9)
    n_iter = 9
    grid_size = 8
    expected_warning = (
        "The total space of parameters %d is smaller "
        "than n_iter=%d. Running %d iterations. For "
        "exhaustive searches, use GridSearchCV." % (grid_size, n_iter, grid_size)
    )
    with pytest.warns(UserWarning, match=expected_warning):
        list(sampler)

    # degenerates to GridSearchCV if n_iter the same as grid_size
    sampler = ParameterSampler(params, n_iter=8)
    samples = list(sampler)
    assert len(samples) == 8
    for values in ParameterGrid(params):
        assert values in samples
    assert len(ParameterSampler(params, n_iter=1000)) == 8

    # test sampling without replacement in a large grid
    params = {"a": range(10), "b": range(10), "c": range(10)}
    sampler = ParameterSampler(params, n_iter=99, random_state=42)
    samples = list(sampler)
    assert len(samples) == 99
    hashable_samples = ["a%db%dc%d" % (p["a"], p["b"], p["c"]) for p in samples]
    assert len(set(hashable_samples)) == 99

    # doesn't go into infinite loops
    params_distribution = {"first": scipy_stats.bernoulli(0.5), "second": ["a", "b", "c"]}
    sampler = ParameterSampler(params_distribution, n_iter=7)
    samples = list(sampler)
    assert len(samples) == 7
