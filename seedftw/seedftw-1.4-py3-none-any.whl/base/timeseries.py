"""
Functions related to timeseries management.

This file can also be imported as a module and contains the following
functions:

    * format_to_timetable - converts wind speed to power output of a wind turbine
    * synchronise - convert solar irradiance to the power output of a PV installation
    * resample_timeseries - resamples a timeseries to a given resolution
    * split_in_daily_profiles - splits a timeseries in a set of daily profiles
    * split_timeseries_in_chunks - splits a timeseries in chunks of data
    * timestep_start - determines a timestep start for a given resolution
    * now - determines a the current time (floored to a given resolution)
    * datetime_to_microepoch - converts a datetime to microepoch
    * microepoch_to_datetime_index - converts microepoch to datetime
    * microepoch_to_local_datetime - converts microepoch to a local datetime
    
"""

from datetime import datetime, timedelta
from typing import Any

import numpy as np

# Import all useful libraries
import pandas as pd
from dateutil.tz import tzlocal
from pytz import timezone

from .types import (
    timezone_input,
    timezone_output,
    dict_or_none,
    bool_or_none,
    str_or_none,
    datetime_or_none,
)


# Helpers
def __is_timezone(var: Any) -> bool:
    class_name = str(var.__class__)
    return class_name.startswith("<class 'pytz.tzfile.") or class_name.startswith(
        "<class 'dateutil.tz.tz."
    )


def __get_local_timezone() -> timezone_output:
    return tzlocal()


# Dealing with timeseries data
def format_to_timetable(
    data: pd.DataFrame,
    time_column: str = "t",
    column_dict: dict_or_none = None,
    inplace: bool = False,
    infer_datetime: bool = True,
    utc_index: bool_or_none = None,
):
    """Formats a pandas dataframe into a timetable

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe to convert to timetable
    time_column : str
        Name of the column to use as time index
        (default: "t")
    column_dict : dict
        Dictionary to use for column renaming, if needed
        (default: None)
    inplace : Boolean
        Whether or not to operate the formatting in place
        (default: False)
    infer_datetime : Boolean
        Whether or not to infer the datetime format from the first element.
        See pandas.to_datetime() documentation for more details
        (default: True (for speed considerations in API context) )
    utc_index : Boolean
        If True, ensures that the timezone is defined to UTC on the index (time_column)
        (default: None)

    Raises
    ------
    None

    Returns
    -------
    data : pd.DataFrame
        DataFrame indexed by time (timetable)
        (None - if inplace is True)
    """

    if inplace is True:
        d = data
    else:
        d = data.copy()

    if len(d) > 0:
        if column_dict is not None:
            d.rename(columns=column_dict, inplace=True)

        if time_column != "t":
            d.rename(columns={time_column: "t"}, inplace=True)

        if isinstance(d["t"][0], str):
            d["t"] = pd.to_datetime(
                d["t"], infer_datetime_format=infer_datetime, utc=utc_index
            )

        d.set_index("t", inplace=True)
        d.sort_index(ascending=True, inplace=True)

    if inplace is True:
        return None
    else:
        return d


def synchronise(
    df1: pd.DataFrame, df2: pd.DataFrame, base: str = "first", fill: str_or_none = None
):
    """Formats a pandas dataframe into a timetable

    Parameters
    ----------
    df1 : pd.DataFrame
        First DataFrame to merge
    df2 : pd.DataFrame
        First DataFrame to merge
    base : str
        Time base for the merged DataFrame
        (options: "first","second","intersection","union")
        (default: "first")
    fill : str
        Filling method, if relevant
        (options: "backfill")
        (default: None)

    Raises
    ------
    None

    Returns
    -------
    data : pd.DataFrame
        DataFrame indexed by time (timetable)
    """

    # Some more hints here: https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#resampling

    if base == "first":
        df_m = df1.merge(df2, how="left", right_index=True, left_index=True)

    elif base == "second":
        df_m = df1.merge(df2, how="right", right_index=True, left_index=True)

    elif base == "intersection":
        df_m = df1.merge(df2, how="intersection", right_index=True, left_index=True)

    elif base == "union":
        df_m = df1.merge(df2, how="outer", right_index=True, left_index=True)

    else:
        raise Exception(f"This case is not supported : {base}")

    if fill is not None:
        if fill == "backfill":
            df_m = df_m.fillna("backfill", axis="index")
        else:
            raise Exception(f"This fill is not supported yet: {fill}")

    return df_m


def resample_timeseries(
    data: pd.DataFrame,
    resolution: str = "raw",
    function: str = "mean",
    tz: timezone_input = None,
    **kwargs,
) -> pd.DataFrame:
    """Resamples a timeseries at a given frequency

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame to resample
    resolution : str
        Resolution to use for the daily profile
        (options: "raw","hour","day")
        (default: "raw")
    function : str
        Function to use for the resampling
        (options: "mean","min","max","sum")
        (default: "mean")
    tz : str, pytz timezone, or None
        Time-zone for the daily profile
        If None is specified, or if the index is timezone-naive, this is skipped
        (default: None)

    Raises
    ------
    None

    Returns
    -------
    T_split : pd.DataFrame
        DataFrame of containing the split of the daily profiles, indexed by date
    """

    need_to_reset_timezone = False
    target_tz = __backwards_compatibility_tz(tz=tz, legacy_tz=kwargs.get("timezone"))

    if resolution == "raw" or data is None or len(data) == 0:
        None

    else:
        if resolution == "hour":
            resampler = data.resample("H")
        elif resolution == "day":
            if target_tz is None:
                resampler = data.resample("D")
            else:
                # Averaging per day is made in local timezone
                data.index = data.index.tz_convert(target_tz)
                resampler = data.resample("D")
                need_to_reset_timezone = True

        else:
            raise Exception(f"Illegal value of data resolution: {resolution}")

        if function == "mean":
            data = resampler.mean()
        elif function == "sum":
            data = resampler.sum()
        elif function == "min":
            data = resampler.min()
        elif function == "max":
            data = resampler.max()
        else:
            raise Exception(f"Illegal value of function: {function}")

    if need_to_reset_timezone is True:
        data.index = data.index.tz_convert("UTC")

    return data


def split_in_daily_profiles(
    data: pd.DataFrame,
    column: str,
    resolution: str = "hour",
    tz: str_or_none = None,
    aggregate: str = "mean",
    **kwargs,
) -> pd.DataFrame:
    """Formats a pandas dataframe into a timetable

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame to split in daily profiles
    column : str
        Name of the column to split in daily profiles
    resolution : str
        Resolution to use for the daily profile
        (options: "hour","15min","10min","5min")
        (default: "hour")
    tz : str, pytz timezone, or None
        Time-zone for the daily profile
        If None is specified, or if the index is timezone-naive, this is skipped
        (default: None)
    aggregate : str
        How to aggregate points if downsampling
        (options: "mean", "sum")
        (default: "mean")

    Raises
    ------
    None

    Returns
    -------
    T_split : pd.DataFrame
        DataFrame of containing the split of the daily profiles, indexed by date
    """
    target_tz = __backwards_compatibility_tz(tz=tz, legacy_tz=kwargs.get("time_zone"))

    data_copy = data[[column]].copy()
    data_copy["date"] = data_copy.index.date

    if target_tz is not None:
        data_copy.index = data_copy.index.tz_convert(target_tz)

    T_split = (
        pd.DataFrame({"date": data_copy.index.date})
        .drop_duplicates(subset=["date"])
        .set_index("date")
    )

    if resolution == "hour":
        data_copy["timeOfDay"] = data_copy.index.hour
        range2use = range(0, 24, 1)
        col_name = lambda x: "H" + str(x)

    elif resolution == "30min":
        data_copy["timeOfDay"] = data_copy.index.hour * 60 + data_copy.index.minute
        range2use = range(0, 24 * 60, 30)
        col_name = lambda x: "M15_" + str(int(x / 30))

    elif resolution == "15min":
        data_copy["timeOfDay"] = data_copy.index.hour * 60 + data_copy.index.minute
        range2use = range(0, 24 * 60, 15)
        col_name = lambda x: "M15_" + str(int(x / 15))

    elif resolution == "10min":
        data_copy["timeOfDay"] = data_copy.index.hour * 60 + data_copy.index.minute
        range2use = range(0, 24 * 60, 10)
        col_name = lambda x: "M10_" + str(int(x / 10))

    elif resolution == "5min":
        data_copy["timeOfDay"] = data_copy.index.hour * 60 + data_copy.index.minute
        range2use = range(0, 24 * 60, 5)
        col_name = lambda x: "M5_" + str(int(x / 5))

    else:
        raise Exception("Illegal resolution: " + resolution)

    for i in range2use:
        T_i = data_copy[[column, "date"]].loc[data_copy["timeOfDay"] == i]
        if aggregate == "sum":
            T_i = T_i.groupby(["date"]).sum()
        elif aggregate == "mean":
            T_i = T_i.groupby(["date"]).mean()
        else:
            raise Exception(f"Illegal value of aggregate ({aggregate})")
        T_i = T_i.rename(columns={column: col_name(i)})
        T_split = T_split.merge(T_i, how="left", right_index=True, left_index=True)

    return T_split


def split_data_loading_range(
    start: datetime, end: datetime, step: timedelta = timedelta(weeks=24)
):
    date_range = []
    max_date = lambda x: np.min([end, x + step])
    time_1 = start
    time_2 = start
    while time_2 < end:
        time_1 = time_2
        time_2 = max_date(time_1)
        date_range.append([time_1, time_2])

    return date_range


def split_timeseries_in_chunks(timeseries: pd.Series, length: int) -> pd.DataFrame:
    """
    Formats a pandas series into chunks (e.g. for machine learning usages)

    Parameters
    ----------
    timeseries : pd.Series
        Timeseries to split in chunks
    length : int
        Length of the chunks

    Raises
    ------
    None

    Returns
    -------
    chunks_df : pd.DataFrame
        DataFrame of chunks (columns names [x0, x1, ..., xN] where N=length-1)
    """
    chunks_df = pd.DataFrame()
    for i in range(0, length):
        chunks_df[f"x{i}"] = timeseries.shift(-i)
    return chunks_df


def timestep_start(
    step: str, t: datetime_or_none = None, tz: timezone_input = __get_local_timezone()
) -> datetime:

    if t is None:
        t = datetime.now(tz)

    if step == "raw":
        t_start = t
    elif step in ["second", "1s"]:
        t_start = t.replace(microsecond=0)
    elif step == "15s":
        sec_start = int(t.second / 15) * 15
        t_start = t.replace(microsecond=0, second=sec_start)
    elif step == "30s":
        sec_start = int(t.second / 30) * 30
        t_start = t.replace(microsecond=0, second=sec_start)
    elif step in ["minute", "1min"]:
        t_start = t.replace(microsecond=0, second=0)
    elif step == "5min":
        min_start = int(t.minute / 5) * 5
        t_start = t.replace(microsecond=0, second=0, minute=min_start)
    elif step == "15min":
        min_start = int(t.minute / 15) * 15
        t_start = t.replace(microsecond=0, second=0, minute=min_start)
    elif step == "30min":
        min_start = int(t.minute / 30) * 30
        t_start = t.replace(microsecond=0, second=0, minute=min_start)
    elif step in ["hour", "1h"]:
        t_start = t.replace(microsecond=0, second=0, minute=0)
    elif step in ["day", "1d"]:
        t_start = t.replace(microsecond=0, second=0, minute=0, hour=0)
    elif step == "month":
        t_start = t.replace(microsecond=0, second=0, minute=0, hour=0, day=1)
    elif step == "year":
        t_start = t.replace(microsecond=0, second=0, minute=0, hour=0, day=1, month=1)
    else:
        raise Exception(f"Unknown step: {step}")

    return t_start


def now(step: str = "raw", tz: timezone_input = __get_local_timezone()) -> datetime:
    return timestep_start(step, t=None, tz=tz)


# Functions dealing with microepoch data
def datetime_to_microepoch(datetimes2use: datetime) -> int:
    return int(datetimes2use.timestamp() * 1e6)


def microepoch_to_datetime_index(microepoch: pd.Series) -> pd.DatetimeIndex:
    t = pd.DatetimeIndex(np.round(microepoch).astype("datetime64[us]"))
    return t.tz_localize("UTC")


def microepoch_to_local_datetime(microepoch) -> pd.Series:
    t = pd.Datetime(np.round(microepoch).astype("datetime64[us]"))
    return t.tz_localize(__get_local_timezone())


# For backwards compatibility
def __backwards_compatibility_tz(
    tz: timezone_input = None, legacy_tz: timezone_input = None
) -> timezone_output:
    if legacy_tz is None:
        tz_out = tz
    else:
        if tz is None:
            tz_out = legacy_tz
        else:
            raise Exception(
                """Parameter name used for timezone is only used for backwards compatibility -
                please update to 'tz' to support future standard"""
            )

    if tz_out is None:
        return None
    elif isinstance(tz_out, str):
        return timezone(tz_out)
    elif __is_timezone(tz_out):
        return tz_out
    else:
        raise Exception(
            "Invalid format for input 'time_zone' (must be either str or pytz timezone)"
        )
