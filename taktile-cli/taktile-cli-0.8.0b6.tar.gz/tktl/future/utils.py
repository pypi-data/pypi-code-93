import typing as t

import pandas as pd  # type: ignore

from tktl.core.loggers import LOG

JSONObject = t.Dict[t.AnyStr, t.Any]
JSONArray = t.List[t.Any]
JSONStructure = t.Union[JSONArray, JSONObject]


def coerce_dataframe_to_series(df: pd.DataFrame) -> t.Union[pd.DataFrame, pd.Series]:
    if len(df.columns) == 1:
        # Since we store dataframes in parquet files, we assume that a
        # one column dataframe used to be a Series.
        return df.iloc[:, 0]
    return df


def coerce_series_to_dataframe(obj: t.Union[pd.DataFrame, pd.Series]) -> pd.DataFrame:
    if isinstance(obj, pd.Series):
        return pd.DataFrame({str(obj.name): obj})
    if len(obj.columns) == 1:
        LOG.error(
            "Storing 1 column dataframe, this will become a Series on the way back"
        )
    return obj
