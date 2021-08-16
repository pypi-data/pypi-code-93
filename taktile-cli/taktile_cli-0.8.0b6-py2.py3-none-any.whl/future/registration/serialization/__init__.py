import typing as t
from functools import singledispatch

import numpy as np
import pandas as pd  # type: ignore

from tktl.future.registration.exceptions import SerializationError
from tktl.future.utils import JSONStructure

from .dataframe import (  # noqa: F401
    dataframe_deserialize,
    dataframe_serialize,
    dataframe_to_example,
)
from .numpy import numpy_deserialize, numpy_serialize, numpy_to_example  # noqa: F401
from .series import (  # noqa: F401
    series_deserialize,
    series_serialize,
    series_to_example,
)


@singledispatch
def serialize(value: t.Union[np.ndarray, pd.Series, pd.DataFrame]):
    raise SerializationError(f"Can't serialize value of type {type(value)}")


@serialize.register
def _serialize_numpy(value: np.ndarray):
    return numpy_serialize(value=value)


@serialize.register
def _serialize_series(value: pd.Series):
    return series_serialize(value=value)


@serialize.register
def _serialize_dataframe(value: pd.DataFrame):
    return dataframe_serialize(value=value)


@singledispatch
def deserialize(
    sample: t.Union[np.ndarray, pd.Series, pd.DataFrame], *, value: JSONStructure,
):
    raise SerializationError(f"Can't deserialize value of type {type(sample)}")


@deserialize.register
def _deserialize_numpy(sample: np.ndarray, *, value: JSONStructure):
    return numpy_deserialize(value=value, sample=sample)


@deserialize.register
def _deserialize_series(sample: pd.Series, *, value: JSONStructure):
    return series_deserialize(value=value, sample=sample)


@deserialize.register
def _deserialize_dataframe(sample: pd.DataFrame, *, value: JSONStructure):
    return dataframe_deserialize(value=value, sample=sample)


@singledispatch
def to_example(value: t.Union[np.ndarray, pd.Series, pd.DataFrame]):
    raise SerializationError(f"Can't create example value of type {type(value)}")


@to_example.register
def _to_example_numpy(value: np.ndarray):
    return numpy_to_example(value=value)


@to_example.register
def _to_example_series(value: pd.Series):
    return series_to_example(value=value)


@to_example.register
def _to_example_dataframe(value: pd.DataFrame):
    return dataframe_to_example(value=value)
