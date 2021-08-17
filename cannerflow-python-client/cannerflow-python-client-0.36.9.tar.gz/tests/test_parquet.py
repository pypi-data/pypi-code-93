import datetime
import os
import pandas as pd
import pytz
import logging
from cannerflow.utils import *
from numpy import ndarray
from pandas import DataFrame, Timestamp
from .config import TestConfig


ans = {
    "cbool": True,
    "ctinyint": pow(2, 7) - 1,
    "csmallint": pow(2, 15) - 1,
    "cint": pow(2, 31) - 1,
    "cbigint": pow(2, 62),
    "creal": 10.3,
    "cdouble": 10.3,
    "cdecimal": 100.34,
    "cvarchar": "abcdefghijk",
    "cchar": "abcdefghijk",
    "cvarbinary": b"abcdefghijk",
    "cjson": '{"a":1,"b":2}',
    "cdate": Timestamp("2001-08-22"),
    "ctimestamp": Timestamp(
        datetime.datetime.strptime("2001-08-21 19:04:05.321000", "%Y-%m-%d %H:%M:%S.%f")
    ).tz_localize(None),
    "ctimestampwithtz": "2001-08-22 03:04:05.321 America/Los_Angeles",
    "carray": [1, 2, 3],
    "cmap": {b"foo": b"foo1", b"boo": b"boo1"},
    "cipaddress": "10.0.0.1",
    "cuuid": "12151fd2-7586-11e9-8f9e-2a86e4085a59",
    "crow.x": 1,
    "crow.y": 2.0,
}


def test_parquet_to_list():
    df = pd.read_parquet(TestConfig.SAMPLE_PARQUET_FILE, engine="fastparquet")
    columns = list(map(lambda column: {"name": column}, df.columns))
    data = list(
        data_factory(data_format="list", columns=columns, data=df.to_numpy().tolist())
    )
    assert len(ans) == len(data[0]), (
        "the number of elements expected: "
        + str(len(ans))
        + " but actual: "
        + str(len(data[0]))
    )
    for i in range(len(data[0])):
        actual = data[1][i]
        # TODO: ignore the precision issue for now, we would fix it in the future.
        # Expected 10.3 but actual is 10.300000190734863.
        if data[0][i] == "creal":
            actual = round(actual, 2)
        expected = ans[data[0][i]]

        assert actual == expected, (
            "data["
            + str(i)
            + "] expected: "
            + str(ans[data[0][i]])
            + " but actual: "
            + str(data[1][i])
        )


def test_parquet_to_df():
    df = pd.read_parquet(TestConfig.SAMPLE_PARQUET_FILE, engine="fastparquet")
    columns = list(map(lambda column: {"name": column}, df.columns))
    data = DataFrame(
        data_factory(data_format="df", columns=columns, data=df.to_numpy().tolist())
    )
    assert len(ans) == len(data.columns), (
        "the number of elements expected: "
        + str(len(ans))
        + " but actual: "
        + str(len(data[0]))
    )
    for i in range(len(data.columns)):
        actual = data[data.columns[i]][0]
        # same as `test_parquet_to_list`
        if data.columns[i] == "creal":
            actual = round(actual, 2)
        expected = ans[data.columns[i]]

        assert actual == expected, (
            "data["
            + str(i)
            + "] expected: "
            + str(ans[data.columns[i]])
            + " but actual: "
            + str(data[data.columns[i]].values[0])
        )


def test_parquet_to_np():
    df = pd.read_parquet(TestConfig.SAMPLE_PARQUET_FILE, engine="fastparquet")
    columns = list(map(lambda column: {"name": column}, df.columns))
    data = data_factory(data_format="np", columns=columns, data=df.to_numpy().tolist())
    assert len(ans) == len(df.columns), (
        "the number of elements expected: "
        + str(len(ans))
        + " but actual: "
        + str(len(df.columns))
    )
    for i in range(len(df.columns)):
        actual = data[0][i]
        # same as `test_parquet_to_list`
        if df.columns[i] == "creal":
            actual = round(actual, 2)
        expected = ans[df.columns[i]]

        assert actual == expected, (
            "data["
            + str(i)
            + "] expected: "
            + str(ans[df.columns[i]])
            + " but actual: "
            + str(data[0][i])
        )
