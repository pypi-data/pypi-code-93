from pydatamocker.types.datetime import base_props
import pytest
from pydatamocker.types.number import get_sample
from .asserts import assert_equals


PROPS = {
    'mean': 10,
    'std': 3,
    'n': 10,
    'p': 0.3,
    'min': 10,
    'max': 30,
    'start': 30,
    'end': 5000,
    'round': 4
}


MOCK_TYPE_TREE = {
    'float': {'uniform', 'normal', 'range'},
    'integer': {'uniform', 'binomial', 'range'}
}

PROPS_MIN_CONFIGS = {
    'uniform': [
        {'min': -323 }, {'max': 9311}, {}
    ],
    'range': [
        {'start': -314}, {'end': 12323}, {}
    ]
}


SAMPLE_SIZE = 320030


def _assert_no_na(sample, type_, distr):
    assert_equals(0, sample.isna().sum(), f"NaN values are present in the series. Type: {type_}, Distribution: {distr}")


def test_no_nans():
    for type_, distributions in MOCK_TYPE_TREE.items():
        for distr in distributions:
            sample = get_sample(type_, SAMPLE_SIZE, **{**PROPS, 'distr': distr})
            _assert_no_na(sample, type_, distr)


def test_base_props():
    for type_ in ('integer', 'float'):
        for distr in ('uniform', 'range'):
            for props in PROPS_MIN_CONFIGS[distr]:
                sample = get_sample(type_, SAMPLE_SIZE, **props)
                _assert_no_na(sample, type_, distr)
