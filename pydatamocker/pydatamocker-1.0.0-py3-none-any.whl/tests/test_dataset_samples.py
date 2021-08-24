import pytest
from pydatamocker.types.dataset import get_dataset_sample, DATASET_KEYS
from .asserts import assert_equals


SAMPLE_SIZE = 103214


def test_no_nans_dataset():
    for dataset in DATASET_KEYS:
        sample = get_dataset_sample(dataset, SAMPLE_SIZE)
        assert_equals(0, sample.isna().sum(), f"Sample has NaN values. Dataset: {dataset}")
