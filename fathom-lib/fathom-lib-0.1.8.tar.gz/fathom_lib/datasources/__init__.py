import pathlib

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class DataFrame(BaseEstimator, TransformerMixin):
    """Trivial transformer as starting block"""

    def fit(self, X, y=None):
        print(f"{self}.fit()")
        return self

    def transform(self, X: pd.DataFrame, y=None):
        print(f"{self}.transform()")
        return X


def load_dummy_data():
    this_folder = pathlib.Path(__file__).parent.absolute()
    df = pd.read_csv(this_folder / "example_data.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"] * 1_000_000)
    df = df.sort_values("timestamp")
    df["next_failure_in_30_days"].fillna(31, inplace=True)
    df["next_failure_in_30_days"] = (df["next_failure_in_30_days"] < 30).astype(np.int)
    return df


def load_dummy_regression_data():
    this_folder = pathlib.Path(__file__).parent.absolute()
    df = pd.read_csv(this_folder / "example_data.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"] * 1_000_000)
    df = df.sort_values("timestamp")
    df["next_failure_in_30_days"].fillna(31, inplace=True)
    return df


def load_sensor_data():
    this_folder = pathlib.Path(__file__).parent.absolute()
    df = pd.read_csv(this_folder / "sensor_data.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df
