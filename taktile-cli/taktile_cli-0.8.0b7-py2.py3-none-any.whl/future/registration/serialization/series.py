import json
import typing as t

import pandas as pd  # type: ignore

from tktl.future.utils import JSONStructure


def series_deserialize(*, value: JSONStructure, sample: pd.Series) -> pd.Series:
    return pd.Series(value)


def series_serialize(*, value: pd.Series) -> JSONStructure:
    return value.to_list()


def series_to_example(*, value: pd.Series) -> t.Any:
    return json.dumps(value.iloc[[0]].to_list())
