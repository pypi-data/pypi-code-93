import pytest
from pydatamocker.types.enum import *
from .asserts import assert_equals, assert_subset


SAMPLE_SIZE = 320030


PROPS = [
    {
        'values': [1, 9, 5, 6, 7, -1, 19],
        'weights': [3, 5, 6, 7, 3, 2, 10]
    },
    {
        'values': ['Rick', 'Morty', 'plumbus', 'CONSTANT'],
        'weights': [0.3, 0.2, 0.2, 0.1]
    }
]


def test_sample_is_subset():
    for props in PROPS:
        uniques_set = set(get_sample(SAMPLE_SIZE, **props).unique())
        vals = props['values']
        vals_set = set(vals)
        assert uniques_set.issubset(vals_set), f"Unique values in the sample of choices {vals} are not the subset of the choices"


def test_dependent_is_subset():
    vals = ['a', 'b', 'c']
    ctrl = get_sample(SAMPLE_SIZE, values=vals, weights=[1, 1, 1])
    dep_vals ={
        'a': [10, 20, 30],
        'b': [200, 600, 800],
        'c': ['c', 'd']
    }
    dep_sample = get_dependent_sample(ctrl, values=dep_vals)
    assert_equals(SAMPLE_SIZE, len(dep_sample), 'Dependent sample has incorrect size')
    df = DataFrame({ 'ctrl': ctrl, 'dep': dep_sample })
    gr = df.groupby('ctrl')
    for ctrl_val in vals:
        dep_sample_uniques = gr.get_group(ctrl_val)['ctrl'].unique()
        assert_subset(dep_sample_uniques, dep_vals, 'The sample unique value set is not a subset of the specified options')


def test_base_props():
    values = PROPS[0]['values']
    sample = get_sample(SAMPLE_SIZE, values=values)
    assert_subset(sample.unique(), set(values), "The sample values are not a subset of the specified options")
