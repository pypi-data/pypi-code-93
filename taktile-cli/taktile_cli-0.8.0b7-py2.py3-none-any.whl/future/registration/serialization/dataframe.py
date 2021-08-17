import pandas as pd  # type: ignore

from tktl.future.utils import JSONStructure


def dataframe_deserialize(
    *, value: JSONStructure, sample: pd.DataFrame
) -> pd.DataFrame:
    return pd.DataFrame(value)


def dataframe_serialize(*, value: pd.DataFrame) -> str:
    return value.to_json(orient="records", date_format="iso")


def dataframe_to_example(*, value: pd.DataFrame) -> str:
    return value.iloc[[0]].to_json(orient="records", date_format="iso")
