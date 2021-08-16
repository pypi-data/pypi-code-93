"""
Functions related to data loading in Denmark.

API specification is found on:
    https://confluence.govcloud.dk/display/FDAPI/Meteorological+Observation

functions:

    * get_weather_stations - loads the list of all Danish weather stations
    * get_weather_station_data - loads historical data for a given station
    * get_closest_weather_station - identifies the closest weather station
    * get_data_for_coordinates - loads historical data from the closest station
        to a set of coordinates
    * set_api_token - loads the API token

"""

import os
import warnings
from datetime import datetime, timedelta
from functools import lru_cache
from typing import List, Union, Dict

import numpy as np
import pandas as pd
from pytz import utc
from requests import Session, Response
from seedftw.base.timeseries import (
    format_to_timetable,
    datetime_to_microepoch,
    microepoch_to_datetime_index,
    synchronise,
)
from seedftw.base.timeseries import resample_timeseries
from seedftw.base.tricks import split_api_calls
from seedftw.environment.geography import distance_between_coordinates
from seedftw.exceptions import MissingApiKeyError

__dk_timezone = "Europe/Copenhagen"
__env_var_api_token_metobsapi = "SEEDFTW_TOKEN_DK_DMI_METOBSAPI"
__env_var_api_token_metobsapiv2 = "SEEDFTW_TOKEN_DK_DMI_METOBSAPI_V2"
__latest_version = "v2"

__session = Session()


def __warn_deprecation(version="v1"):
    warnings.warn(
        "Usage of this version ({}) will soon be deprecated".format(version),
        PendingDeprecationWarning,
    )


def __unsupported_version(version):
    raise Exception("Unsupported version ({})".format(version))


def set_api_token(
    dmi_metObsAPIv2: Union[str, None] = None, dmi_metObsAPI: Union[str, None] = None
) -> None:
    """Loads the API token for the metObsAPI from the Danish weather stations.

    If you do not have one, go to https://confluence.govcloud.dk/pages/viewpage.action?pageId=26476690 to create one.

    Parameters
    ----------
    dmi_metObsAPIv2 : str
            API token for the metObsAPI (v2).

    dmi_metObsAPI : str
            API token for the metObsAPI (v1 - deprecated).

    Raises
    ------
    None

    Returns
    -------
    None
    """
    if dmi_metObsAPIv2 is not None:
        os.environ[__env_var_api_token_metobsapiv2] = dmi_metObsAPIv2
        # headers = {"Authorization" : "X-Gravitee-Api-Key: " + str(dmi_metObsAPIv2)}
        headers = {"X-Gravitee-Api-Key": str(dmi_metObsAPIv2)}
        __session.headers.update(headers)

    if dmi_metObsAPI is not None:
        __warn_deprecation(version="v1")
        os.environ[__env_var_api_token_metobsapi] = dmi_metObsAPI


def _get_api_key(api: str = "MetObsAPIv2") -> str:

    if api == "MetObsAPI":
        __warn_deprecation(version="v1")
        dmi_api_key = os.getenv(__env_var_api_token_metobsapi)
        if dmi_api_key is None:
            e = MissingApiKeyError(
                message="Missing API key for DMI service.",
                environment_variable=__env_var_api_token_metobsapi,
                create_at_url="https://confluence.govcloud.dk/display/FDAPI",
            )
            raise e
    elif api == "MetObsAPIv2":
        dmi_api_key = os.getenv(__env_var_api_token_metobsapiv2)
        if dmi_api_key is None:
            e = MissingApiKeyError(
                message="Missing API key for DMI service.",
                environment_variable=__env_var_api_token_metobsapi,
                create_at_url="https://confluence.govcloud.dk/display/FDAPI",
            )
            raise e
    else:
        raise Exception("Illegal api input ({})".format(api))

    return dmi_api_key


def __format_data_table(data):
    return format_to_timetable(
        data, time_column="Minutes5UTC", column_dict=None, utc_index=True
    )


# Loading data from DMI's API
def __dmi_api_call(
    address: str, params: Union[Dict, None] = None, version: str = __latest_version
) -> Response:

    if version == "v1":
        __warn_deprecation(version="v1")
        if params is not None:
            raise Exception("Usage of params is not supported in v1")
        api_key_part = "api-key=" + _get_api_key(api="MetObsAPI")
        query_url = "https://dmigw.govcloud.dk/metObs/v1/" + address
        if "?" in query_url:
            binding_sym = "&"
        else:
            binding_sym = "?"
        # Read data in Json format
        url_2_call = query_url + binding_sym + api_key_part
        result = pd.read_json(url_2_call)

    elif version == "v2":
        query_url = "https://dmigw.govcloud.dk/v2/metObs/collections/" + address
        result = __session.get(query_url, params=params).json()

    else:
        __unsupported_version(version)

    return result


# Loading data from the API for 1 parameter
def __sub_load_parameter_timeseries(
    station: Union[str, int],
    parameter: str,
    start: datetime,
    end: datetime,
    version: str = __latest_version,
) -> pd.DataFrame:
    """
    Documentation of the details of the data is available here:
    >>  https://confluence.govcloud.dk/display/FDAPI/Meteorological+Observation
    """

    if isinstance(station, str):
        station_string = station
    else:
        station_string = str(station).zfill(5)

    parameter2id = {
        "ambient_temperature": "temp_dry",
        "wind_speed": "wind_speed",
        "wind_direction": "wind_dir",
        "relative_humidity": "humidity",
        "global_solar_radiation": "radia_glob",
    }

    # Adding a query size limiter to approx. 6 months
    limit2use = 30000

    if version == "v1":
        start_microepoch = datetime_to_microepoch(start)
        end_microepoch = datetime_to_microepoch(end)
        query_url = (
            "observation?from={}&to={}&stationId={}&parameterId={}&limit={}".format(
                str(start_microepoch),
                str(end_microepoch),
                station_string,
                parameter2id[parameter],
                str(limit2use),
            )
        )
        params = None
    elif version == "v2":

        def __dateformat(t):
            return t.astimezone(utc).isoformat(timespec="seconds", sep="T")

        query_url = "observation/items"
        params = {
            "datetime": "{}/{}".format(__dateformat(start), __dateformat(end)),
            "stationId": station_string,
            "parameterId": parameter2id[parameter],
            "limit": str(limit2use),
        }
    else:
        __unsupported_version(version)

    if version == "v1":
        dmi_raw_data = __dmi_api_call(query_url, params=params, version="v1")
        dmi_raw_data["t"] = microepoch_to_datetime_index(dmi_raw_data["timeObserved"])
    elif version == "v2":
        dmi_raw_data_json = __dmi_api_call(query_url, params=params, version="v2")
        dmi_raw_data = pd.DataFrame(dmi_raw_data_json["features"])["properties"].apply(
            pd.Series
        )
        dmi_raw_data["t"] = dmi_raw_data["observed"]
    else:
        __unsupported_version(version)

    data = format_to_timetable(
        dmi_raw_data[["t", "value"]],
        time_column="t",
        column_dict={"value": parameter},
        utc_index=True,
    )

    if version == "v2":
        data.sort_index(axis=0, inplace=True, ascending=True)

    return data


def __load_parameter_timeseries(
    station, parameter, start, end, resolution, version=__latest_version
):

    # Split calls
    max_step = timedelta(weeks=24)
    margin_last = timedelta(seconds=1)

    def func(t0, t1):
        return __sub_load_parameter_timeseries(
            station,
            parameter,
            t0,
            t1,
            version=version,
        )

    data = split_api_calls(func, start, end, max_step, margin_last)

    # Resample
    data = resample_timeseries(
        data, resolution=resolution, function="mean", tz=__dk_timezone
    )

    return data


@lru_cache(maxsize=2)
def __raw_load_weather_stations(version: str = __latest_version) -> pd.DataFrame:
    if version == "v1":
        call2use = "station?country=DNK"
        df = __dmi_api_call(call2use, params=None, version="v1")
        stations = df["location"].apply(pd.Series)
        focus_pars = ["name", "type", "stationId"]
        stations[focus_pars] = df[focus_pars]

    elif version == "v2":
        call2use = "station/items"
        res = __dmi_api_call(call2use, params=None, version="v2")
        stations = pd.DataFrame(res["features"])["properties"].apply(pd.Series)
        stations["type"] = pd.DataFrame(res["features"])["type"].apply(pd.Series)
        stations[["longitude", "latitude"]] = (
            pd.DataFrame(res["features"])["geometry"]
            .apply(pd.Series)["coordinates"]
            .tolist()
        )
        stations["validTo"] = pd.to_datetime(
            stations["validTo"], infer_datetime_format=True, utc=True
        )
        stations["validFrom"] = pd.to_datetime(
            stations["validFrom"], infer_datetime_format=True, utc=True
        )
        stations["operationTo"] = pd.to_datetime(
            stations["operationTo"], infer_datetime_format=True, utc=True
        )
        stations["operationFrom"] = pd.to_datetime(
            stations["operationFrom"], infer_datetime_format=True, utc=True
        )

    else:
        __unsupported_version(version)

    return stations


def get_weather_stations(
    only_available: bool = False,
    version: str = __latest_version,
    valid_since: Union[None, datetime] = None,
) -> pd.DataFrame:
    """Loads the list of the Danish weather stations

    Parameters
    ----------
    version : version of the DMI API ("v2" or "v1")

    Raises
    ------
    None

    Returns
    -------
    stations : pandas.DataFrame(height,latitude,longitude,name,type,stationId)
        Details of the weather stations
    """
    stations = __raw_load_weather_stations(version=version)

    if version == "v1":
        if only_available is True:
            stations = stations.loc[stations["type"] == "Synop", :]
        if valid_since is not None:
            raise Exception("Usage of valid_since is not supported in version v1")

    elif version == "v2":
        if only_available is True:
            # Filtering all stations not currently available
            k_valid = [np.isnat(x) for x in stations["validTo"].values]
            stations = stations[k_valid]

        if valid_since is not None:
            # Filtering all stations with data start after the allowed minimum
            stations = stations[stations["validFrom"] <= valid_since]
    else:
        __unsupported_version(version)

    return stations


def get_weather_station_data(
    station: Union[int, str] = 6031,
    start: datetime = None,
    end: datetime = None,
    resolution: str = "hour",
    parameters: List[str] = ["ambient_temperature"],
    version: str = __latest_version,
) -> pd.DataFrame:
    """Loads historical data for a given weather station

    Parameters
    ----------
    station : int or str
        stationId of the station for which data is to be loaded
    start : datetime
        Time for the start of the historical period
    end: datetime
        Time for the end of the historical period
    resolution: str
        Resolution of the data to load (raw,hour,day)
    parameters : list(str)
        List of parameters to be loaded
        (Options: "ambient_temperature","wind_speed","wind_direction",
         "relative_humidity","global_solar_radiation")
    version : version of the DMI API ("v2" or "v1")

    Raises
    ------
    None

    Returns
    -------
    data : pandas.DataFrame(t,ambient_temperature)
        Timetable of the ambient temperature [degrees C]


    Documentation of the details of the data is available here:
    >>  https://confluence.govcloud.dk/pages/viewpage.action?pageId=26476616

    """

    if start is None:
        start = datetime.now() - timedelta(days=3)
    if end is None:
        end = datetime.now()

    data = None

    for par_i in parameters:
        data_i = __load_parameter_timeseries(
            station, par_i, start, end, resolution, version=version
        )
        if data is None:
            data = data_i
        else:
            data = synchronise(data, data_i, "union")

    return data


def get_closest_weather_station(
    latitude: float,
    longitude: float,
    version: str = __latest_version,
    country: str = "dk",
) -> pd.Series:
    """Identifies the closest weather station for a set geographical coordinates

    Parameters
    ----------
    latitude : float
        Latitude [degrees]
    longitude : float
        Longitude [degrees]
    version : version of the DMI API ("v2" or "v1")

    Raises
    ------
    None

    Returns
    -------
    closest_station : pandas.Series(height,latitude,longitude,name,type,stationId)
        Details of the closest location
    """

    # Get all DMI locations
    selected_stations = get_weather_stations(only_available=True, version=version)

    if version == "v2":
        selected_stations = selected_stations[
            [("temp_dry" in s_i) for s_i in selected_stations["parameterId"]]
        ]

        low_country = country.lower()
        if low_country in ["dk", "dnk", "denmark"]:
            selected_stations = selected_stations[selected_stations["country"] == "DNK"]
        else:
            raise Exception("Unsupported land ({})".format(country))

    distance_to_stations = selected_stations.apply(
        lambda row: distance_between_coordinates(
            [latitude, longitude], [row["latitude"], row["longitude"]]
        ),
        axis=1,
    )

    closest_index = selected_stations.index[np.argmin(distance_to_stations)]
    closest_station = selected_stations.loc[closest_index, :]

    return closest_station


def get_data_for_coordinates(
    latitude: str = 57.046707,
    longitude: str = 9.935932,
    start: datetime = (datetime.now() - timedelta(days=3)),
    end: datetime = datetime.now(),
    resolution: str = "hour",
    parameters: List[str] = ["ambient_temperature"],
    version: str = __latest_version,
) -> pd.DataFrame:
    """Loads historical data from the closest weather station to a set of coordinates

    Parameters
    ----------
    latitude : float
        Latitude [degrees]
    longitude : float
        Longitude [degrees]
    start : datetime
        Time for the start of the historical period
    end: datetime
        Time for the end of the historical period
    resolution: str
        Resolution of the data to load (raw,hour,day)
    parameters : list(str)
        List of parameters to be loaded
        (Options: "ambient_temperature","wind_speed","wind_direction",
         "relative_humidity","global_solar_radiation")
    version : version of the DMI API ("v2" or "v1")

    Raises
    ------
    None

    Returns
    -------
    data : pandas.DataFrame(t,ambient_temperature)
        Timetable of the ambient temperature [degrees C]
    """

    closest_station = get_closest_weather_station(latitude, longitude, version=version)
    data = get_weather_station_data(
        station=closest_station["stationId"],
        start=start,
        end=end,
        resolution=resolution,
        parameters=parameters,
        version=version,
    )
    return data
