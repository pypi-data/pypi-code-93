# -*- coding: utf-8 -*-
"""
Functions related to data loading in Great Britain.

Sources:
- https://carbonintensity.org.uk/

"""

from datetime import timedelta

# For caching
from functools import lru_cache

import numpy as np
import pandas as pd
import requests
from dateutil.parser import parse
from seedftw.base.timeseries import (
    format_to_timetable,
    resample_timeseries,
    timestep_start,
    now,
)
from seedftw.base.tricks import split_api_calls

__uk_timezone = "Europe/London"
__api_url = "https://api.carbonintensity.org.uk/"

__api_region_ids = {
    "north scotland": 1,
    "south scotland": 2,
    "north west england": 3,
    "north east england": 4,
    "yorkshire": 5,
    "north wales": 6,
    "south wales": 7,
    "west midlands": 8,
    "east midlands": 9,
    "east england": 10,
    "south west england": 11,
    "south england": 12,
    "london": 13,
    "south east england": 14,
    "england": 15,
    "scotland": 16,
    "wales": 17,
}
# Loading data from CarbonIntensity.org.uk
@lru_cache(maxsize=10)
def __api_call(endpoint):
    r = requests.get(__api_url + endpoint)

    data = r.json()

    if data is None:
        raise Exception(
            "No data returned by the API (on endpoint: {})".format(endpoint)
        )

    if "error" in data.keys():
        status = data["error"]["code"]
    else:
        status = 200

    if status == 200:
        None
    elif status.startswith("400"):
        raise Exception("Bad request (on endpoint: {})".format(endpoint))
    elif status.startswith("500"):
        raise Exception("Internal server error (on endpoint: {})".format(endpoint))
    else:
        raise Exception(
            "Unknown return status={} (on endpoint: {})".format(status, endpoint)
        )

    return data


def __convert_string_to_datetime(string):
    return parse(string)


def get_emission_factors(out="dict"):
    endpoint = "intensity/factors"
    r = __api_call(endpoint)
    data = r["data"][0]

    low_format = out.lower()

    if low_format == "dict":
        return data
    elif low_format == "dataframe":
        return pd.DataFrame(
            {"technology": data.keys(), "emission_intensity": data.values()}
        )
    else:
        raise Exception("Unknown format: " + out)


def __get_regional_api_endpoint(area, start, end):
    if isinstance(area, str):
        if area.lower() in ["england", "wales", "scotland"]:
            endpoint = "regional/intensity/{}/{}/regionid/{}".format(
                start.isoformat(), end.isoformat(), __api_region_ids[area.lower()]
            )
        else:
            endpoint = "regional/intensity/{}/{}/postcode/{}".format(
                start.isoformat(), end.isoformat(), area
            )
    else:
        endpoint = "regional/intensity/{}/{}/regionid/{}".format(
            start.isoformat(), end.isoformat(), str(area)
        )
    return endpoint


def __unpack_region_data(data):
    data_copy = data["data"].copy().apply(pd.Series)
    return data_copy


def __load_historical_intensity(start, end, area):
    if area is None:
        endpoint = "intensity/{}/{}".format(start.isoformat(), end.isoformat())
    else:
        endpoint = __get_regional_api_endpoint(area, start, end)

    r = __api_call(endpoint)
    raw_data = pd.DataFrame(r["data"])

    if "regionid" in raw_data.keys():
        raw_data = __unpack_region_data(raw_data)

    if len(raw_data) == 0:
        raise Exception("No data available")

    raw_data["start"] = pd.to_datetime(raw_data["from"])

    temp_i = raw_data["intensity"].apply(pd.Series)
    raw_data[temp_i.keys()] = temp_i

    for col_i in ["forecast", "actual"]:
        if col_i not in raw_data.keys():
            raw_data[col_i] = np.NaN

    data = format_to_timetable(
        raw_data[["start", "forecast", "actual"]],
        time_column="start",
        column_dict=None,
        utc_index=True,
    )
    return data


def __get_historical_intensity(
    start=None,
    end=None,
    resolution="raw",
    area=None,
):
    if start is None:
        start = timestep_start("30min") - timedelta(days=2)
    elif end is None:
        end = timestep_start("30min")

    max_step = timedelta(days=13)
    fun2use = lambda x, y: __load_historical_intensity(x, y, area)
    data = split_api_calls(
        fun2use,
        start,
        end,
        max_step,
        margin_last=timedelta(seconds=1),
    )

    data = resample_timeseries(
        data, resolution=resolution, function="mean", tz=__uk_timezone
    )
    return data


def __split_demand_percentages(raw_data):
    y = None
    for x_i in raw_data["generationmix"]:
        x_i = pd.DataFrame(x_i).set_index("fuel").transpose()
        if y is None:
            y = x_i
        else:
            y = pd.concat([y, x_i])

    y.index = raw_data.index

    for col_i in y:
        raw_data[col_i] = y[col_i]

    raw_data.pop("generationmix")


def __load_historical_generation(start, end, area=None):

    if area is None:
        endpoint = "generation/{}/{}".format(start.isoformat(), end.isoformat())
    else:
        endpoint = __get_regional_api_endpoint(area, start, end)

    r = __api_call(endpoint)
    raw_data = pd.DataFrame(r["data"])

    if "regionid" in raw_data.keys():
        raw_data = __unpack_region_data(raw_data)
        raw_data.pop("intensity")

    raw_data["start"] = pd.to_datetime(raw_data["from"])

    __split_demand_percentages(raw_data)
    raw_data.pop("from")
    raw_data.pop("to")

    data = format_to_timetable(
        raw_data, time_column="start", column_dict=None, utc_index=True
    )
    return data


def get_historical_generation(
    start=None,
    end=None,
    resolution="raw",
    area=None,
):
    if start is None:
        start = timestep_start("30min") - timedelta(days=2)
    elif end is None:
        end = timestep_start("30min")

    max_step = timedelta(days=13)
    fun2use = lambda x, y: __load_historical_generation(x, y, area)
    data = split_api_calls(
        fun2use,
        start,
        end,
        max_step,
        margin_last=timedelta(seconds=1),
    )

    data = resample_timeseries(
        data, resolution=resolution, function="mean", tz=__uk_timezone
    )
    return data


def electricity_average_co2_intensity(
    area=None,
    start=None,
    end=None,
    resolution="raw",
):
    if start is None:
        start = now() - timedelta(hours=168)
    elif end is None:
        end = now()
    return __get_historical_intensity(start, end, resolution, area=area)


def electricity_average_co2_intensity_forecast(
    area=None,
    start=None,
    end=None,
    resolution="raw",
):
    if start is None:
        start = now()
    elif end is None:
        end = now() + timedelta(hours=24)
    return __get_historical_intensity(start, end, resolution, area=area)
