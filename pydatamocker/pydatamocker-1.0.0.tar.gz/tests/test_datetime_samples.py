import pytest
from pydatamocker.types.datetime import get_sample
from .asserts import assert_equals


PROPS = {
    'date': {
        'start': '2019-02-20',
        'end': '2019-03-30'
    },
    'datetime': {
        'start': '2019-02-28T11:30:00Z',
        'end': '2019-03-02T21:30:00Z'
    }
}


MOCK_TYPE_TREE = {
    'date': { 'uniform', 'range' },
    'datetime': { 'uniform', 'range' }
}


SAMPLE_SIZE = 25723


def test_no_nans():
    for type_, distributions in MOCK_TYPE_TREE.items():
        for distr in distributions:
            sample = get_sample(type_, SAMPLE_SIZE, **{ **PROPS[type_], 'distr': distr })
            assert_equals(0, sample.isna().sum(), f"NaN values are present in the series. Type: {type_}, Distribution: {distr}")


def test_base_props():
    for type_ in MOCK_TYPE_TREE.keys():
        sample = get_sample(type_, SAMPLE_SIZE)
        assert sample is not None, "Sample was not created"
        assert_equals(0, sample.isna().sum(), f"Sample has NaN values. Type: {type_}")
