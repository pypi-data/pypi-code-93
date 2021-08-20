import json
import math
from ast import literal_eval
from typing import Dict

import pandas as pd
from pandas.tseries.frequencies import to_offset
from pandas.tseries.offsets import DateOffset
from sklearn.base import BaseEstimator, TransformerMixin


class RollingAggregationWithFreq(BaseEstimator, TransformerMixin):
    _name_to_offset_map = {"days": "D", "hours": "H", "minutes": "M", "seconds": "S"}

    """
    For allowed windows strings see pandas docs:
    https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases

    Parameters
    ----------
    aggs_windows: str
        List of aggregation windows
    freq: str optional
    """

    def __init__(self, **kwargs):
        aggs_windows = kwargs
        if aggs_windows is not None:
            self.aggs_windows = self._parse_windows(aggs_windows)
        else:
            self.aggs_windows = None
        self.freq = None

    def _parse_windows(self, aggs_windows: Dict[str, Dict[str, str]]):
        all_aggregations = []
        for agg, details in aggs_windows.items():
            details = literal_eval(details)
            offset = to_offset(
                str(details["periodLength"])
                + self._name_to_offset_map[details["periodChosen"]]
            )
            for func in details["itemsChosen"]:
                all_aggregations.append((func, offset))
        return all_aggregations

    def fit(self, X, y=None):
        self.freq = self._get_freq(X)
        return self

    def transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        aggregates = [
            self._single_aggregate(X, agg_func, window)
            for agg_func, window in self.aggs_windows
        ]
        return pd.concat(aggregates, axis=1)

    def _single_aggregate(
        self, X: pd.DataFrame, agg_func: str, window: DateOffset
    ) -> pd.DataFrame:
        min_required_periods = self._get_minimum_periods_required(window)
        # min_required_periods is necessary, because by default when offset is used as a window,
        # pandas does not insert NaNs for first rows (for which we are missing earlier rows),
        # but values computed on insufficient amount of rows.
        aggregated = X.rolling(window, min_periods=min_required_periods).agg(agg_func)
        aggregated.columns = [
            f"{col_name}_{agg_func}_last_{self._to_str(window)}"
            for col_name in aggregated.columns
        ]
        return aggregated

    def _get_minimum_periods_required(self, window: DateOffset) -> int:
        return math.ceil(pd.Timedelta(window) / pd.Timedelta(self.freq))

    def _get_freq(self, X: pd.DataFrame) -> DateOffset:
        inferred = (
            X.index.inferred_freq
        )  # inferred works also when no index frequency is set
        return pd.tseries.frequencies.to_offset(inferred)

    def _to_str(self, offset: DateOffset) -> str:
        s = offset.freqstr
        if not s[0].isdigit():
            # because pandas omits "1" character in "1H", "1s" etc and writes "H", "s"
            return "1" + s
        return s


class RollingAggregation(BaseEstimator, TransformerMixin):
    _name_to_offset_map = {"days": "D", "hours": "H", "minutes": "min", "seconds": "S"}

    """
    For allowed windows strings see pandas docs:
    https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases

    Parameters
    ----------
    aggs_windows: str
        List of aggregation windows
    freq: str optional
    """

    def __init__(self, **kwargs):
        aggs_windows = kwargs
        if aggs_windows is not None:
            self.aggs_windows = self._parse_windows(aggs_windows)
        else:
            self.aggs_windows = None

    def _parse_windows(self, aggs_windows: Dict[str, Dict[str, str]]):
        all_aggregations = []
        for agg, details in aggs_windows.items():
            if "periodChosen" not in details or "periodLength" not in details:
                continue
            if isinstance(details, str):
                details = json.loads(details.replace("'", '"'))
            offset = to_offset(
                str(details["periodLength"])
                + self._name_to_offset_map[details["periodChosen"]]
            )
            offset_str = "{}_{}".format(
                details["periodLength"], details["periodChosen"]
            )
            for func in details["itemsChosen"]:
                all_aggregations.append((func, offset, offset_str))
        return all_aggregations

    def fit(self, X, id, timestamp, y=None):
        return self

    def fit_transform(self, X, id, timestamp, y=None):
        return self.transform(X=X, id=id, timestamp=timestamp, y=y)

    def transform(self, X: pd.DataFrame, id, timestamp, y=None) -> pd.DataFrame:
        X = X.copy()
        cols = X.columns
        X["id"] = id
        X["timestamp"] = timestamp

        # preserving the initial order to recreate in new dataframe
        initial_order_df = pd.DataFrame(X, columns=["timestamp", "id"])

        X = X.sort_values(["id", "timestamp"])
        X = X.drop_duplicates(subset=["id", "timestamp"])

        # saving timestamp as dataframe to enable future comparing
        ordered_timestamp_df = X[["timestamp"]].reset_index(drop=True)

        X.set_index("timestamp", inplace=True)

        for col_name in cols:
            for agg_func, offset, offset_str in self.aggs_windows:
                new_col = f"{col_name}_{agg_func}_last_{offset_str}"
                X[new_col] = (
                    X.groupby("id")[col_name]
                    .rolling(offset)
                    .agg(agg_func)
                    .reset_index(0, drop=True)
                    .values
                )

        X.reset_index(drop=True, inplace=True)
        X["timestamp"] = ordered_timestamp_df["timestamp"]

        # recreating initial order
        initial_order_df = pd.merge(
            initial_order_df, X, on=["timestamp", "id"], how="left"
        )

        initial_order_df.drop(cols, axis=1, inplace=True)
        return initial_order_df.drop(["timestamp", "id"], axis=1)

    def _to_str(self, offset: DateOffset) -> str:
        s = offset.freqstr
        if not s[0].isdigit():
            # because pandas omits "1" character in "1H", "1s" etc and writes "H", "s"
            return "1" + s
        return s


if __name__ == "__main__":
    records = [
        {"id": 1, "timestamp": pd.to_datetime("2020-01-01 00:05:00"), "sensor_a": 101},
        {"id": 1, "timestamp": pd.to_datetime("2020-01-01 01:00:00"), "sensor_a": 102},
        {"id": 2, "timestamp": pd.to_datetime("2020-01-01 01:00:00"), "sensor_a": 202},
        {"id": 3, "timestamp": pd.to_datetime("2020-01-01 01:00:00"), "sensor_a": 401},
        {"id": 1, "timestamp": pd.to_datetime("2020-01-01 00:00:00"), "sensor_a": 100},
        {"id": 1, "timestamp": pd.to_datetime("2020-01-01 00:00:00"), "sensor_a": 100},
        {"id": 2, "timestamp": pd.to_datetime("2020-01-01 00:00:00"), "sensor_a": 200},
        {"id": 3, "timestamp": pd.to_datetime("2020-01-01 00:00:01"), "sensor_a": 400},
        {"id": 2, "timestamp": pd.to_datetime("2020-01-01 00:05:00"), "sensor_a": 201},
    ]
    df = pd.DataFrame.from_records(records)

    agg_settings = {
        "aggregation0": {
            "itemsChosen": ["count", "median", "sum"],
            "periodChosen": "minutes",
            "periodLength": 30,
        },
        "aggregation1": {
            "itemsChosen": ["min"],
            "periodChosen": "hours",
            "periodLength": 2,
        },
    }

    agg = RollingAggregation(**agg_settings)
    df_transformed = agg.transform(
        id=df["id"], timestamp=df["timestamp"], X=df[["sensor_a"]]
    )
    print(df)

    print(df_transformed)
