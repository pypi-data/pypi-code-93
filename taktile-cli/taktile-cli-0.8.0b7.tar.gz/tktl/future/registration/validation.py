import typing as t
from functools import singledispatch

import numpy as np
import pandas as pd  # type: ignore

from .exceptions import ValidationError


@singledispatch
def validate(
    value: t.Union[np.ndarray, pd.DataFrame, pd.Series],
    *,
    sample: t.Union[np.ndarray, pd.DataFrame, pd.Series],
) -> t.Union[np.ndarray, pd.DataFrame, pd.Series]:
    raise ValidationError(f"Can't validate value of type: {type(value)}")


@validate.register
def _validate_numpy(
    value: np.ndarray, *, sample: t.Union[np.ndarray, pd.DataFrame, pd.Series]
) -> np.ndarray:
    if type(value) != type(sample):
        raise ValidationError(
            f"Expected value of type {type(sample)}, got {type(value)}"
        )

    if value.shape[1:] != sample.shape[1:]:
        raise ValidationError(
            "Could not validate numpy array shape. "
            f"Value has shape {value.shape[1:]}, expected shape: {sample.shape[1:]}"
        )

    # We choose not to validate the dtypes here

    return value


@validate.register
def _validate_series(
    value: pd.Series, *, sample: t.Union[np.ndarray, pd.DataFrame, pd.Series]
) -> pd.Series:
    if type(value) != type(sample):
        raise ValidationError(
            f"Expected value of type {type(sample)}, got {type(value)}"
        )

    # We choose not to validate the dtypes here

    return value


@validate.register
def _validate_dataframe(
    value: pd.DataFrame, *, sample: t.Union[np.ndarray, pd.DataFrame, pd.Series]
) -> pd.DataFrame:
    if not isinstance(sample, pd.DataFrame):
        raise ValidationError(
            f"Expected value of type {type(sample)}, got {type(value)}"
        )

    # We choose not to validate the dtypes here

    def decode(x: t.Union[str, bytes]) -> str:
        if isinstance(x, bytes):
            return x.decode()
        return x

    value.columns = [decode(x) for x in value.columns]

    sent_columns = {x for x in value.columns.to_list()}  # type: ignore
    expected_columns = {x for x in sample.columns.to_list()}  # type: ignore

    if sent_columns != expected_columns:
        raise ValidationError(
            "Column mismatch:\n"
            f"Missing columns: {expected_columns.difference(sent_columns)},\n"
            f"Superfluos columns: {sent_columns.difference(expected_columns)}."
        )

    value = value[sample.columns.to_list()]  # type: ignore # ordering
    return value.astype(sample.dtypes.to_dict())  # type: ignore # dtypes. TODO: Improve this
