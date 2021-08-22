#!/usr/bin/env python3

import logging
import requests

from datetime import datetime

from pocar.OneCallApi import OneCallApi

# Uncomment this line to suppress warning message due to:
#    InsecureRequestWarning: Unverified HTTPS request is being made.
#    Adding certificate verification is strongly advised.
#    See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
# We get this warning because an HTTP GET request is made with SSL verification disabled
requests.packages.urllib3.disable_warnings()

# Set local logger to the root logger, to inherit root settings
logger = logging.getLogger(__name__)


# Derived Class to handle Hourly weather data API response
# Hourly holds the weather forecast for the next 48 hours in a hourly basis
# Values are for current hour + 47
class OneCallApiHourly(OneCallApi):
    def __init__(self, lat, lon, key):
        super().__init__(lat, lon, key, "current,daily,minutely,alerts")

    def __is_data_available(self, hour, field):
        value = False
        if ("hourly" in self._rawdata) and (field in self._rawdata["hourly"][hour]):
            value = True
        return value

    def __extract_date_field(self, hour, field, metrics=0):
        value = "N/A"
        if self.__is_data_available(hour, field) is True:
            if metrics == 0:
                dt = datetime.fromtimestamp(self._rawdata["hourly"][hour][field])
                value = f"{dt:%Y-%m-%d %H:%M:%S}"
            else:
                value = self._rawdata["hourly"][hour][field]
        logger.debug("Value for %s is: %s", field, value)
        return value

    def __extract_value_field(self, hour, field):
        value = "N/A"
        if self.__is_data_available(hour, field) is True:
            value = self._rawdata["hourly"][hour][field]
        logger.debug("Value for %s is: %s", field, value)
        return value

    def __extract_value_set(self, hour, field, all_values):
        if hour < 0 or hour > 48:
            raise ValueError("The 'hour' argument must be within range [0, 48]")
        elif all_values is True:
            value = [0] * 48  # Initialize the 48 data time values
            for idx in range(48):
                value[idx] = self.__extract_value_field(idx, field)
        else:
            value = self.__extract_value_field(hour, field)
        return value

    def __extract_weather_field(self, hour, field):
        value = "N/A"
        if ("hourly" in self._rawdata) and ("weather" in self._rawdata["hourly"][hour]):
            if field in self._rawdata["hourly"][hour]["weather"][0]:
                value = self._rawdata["hourly"][hour]["weather"][0][field]
        logger.debug("Value for %s is: %s", field, value)
        return value

    def __extract_weather_set(self, hour, field, all_values):
        if hour < 0 or hour > 48:
            raise ValueError("The 'hour' argument must be within range [0, 48]")
        elif all_values is True:
            value = [0] * 48  # Initialize the 48 data time values
            for idx in range(48):
                value[idx] = self.__extract_weather_field(idx, field)
        else:
            value = self.__extract_weather_field(hour, field)
        return value

    def raw_data_hourly(self):
        value = dict()
        if "hourly" in self._rawdata:
            value = self._rawdata["hourly"]
        return value

    def data_time(self, hour=0, metrics=0, all_values=False):
        if hour < 0 or hour > 48:
            raise ValueError("The 'hour' argument must be within range [0, 48]")
        elif all_values is True:
            value = [0] * 48  # Initialize the 48 data time values
            for idx in range(48):
                value[idx] = self.__extract_date_field(idx, "dt", metrics)
        else:
            value = self.__extract_date_field(hour, "dt", metrics)
        return value

    def temp(self, hour=0, all_values=False):
        return self.__extract_value_set(hour, "temp", all_values)

    def feels_like(self, hour=0, all_values=False):
        return self.__extract_value_set(hour, "feels_like", all_values)

    def pressure(self, hour=0, all_values=False):
        return self.__extract_value_set(hour, "pressure", all_values)

    def humidity(self, hour=0, all_values=False):
        return self.__extract_value_set(hour, "humidity", all_values)

    def dew_point(self, hour=0, all_values=False):
        return self.__extract_value_set(hour, "dew_point", all_values)

    def uvi(self, hour=0, all_values=False):
        return self.__extract_value_set(hour, "uvi", all_values)

    def clouds(self, hour=0, all_values=False):
        return self.__extract_value_set(hour, "clouds", all_values)

    def visibility(self, hour=0, all_values=False):
        return self.__extract_value_set(hour, "visibility", all_values)

    def wind_speed(self, hour=0, all_values=False):
        return self.__extract_value_set(hour, "wind_speed", all_values)

    def wind_deg(self, hour=0, all_values=False):
        return self.__extract_value_set(hour, "wind_deg", all_values)

    def wind_gust(self, hour=0, all_values=False):
        return self.__extract_value_set(hour, "wind_gust", all_values)

    def weather_id(self, hour=0, all_values=False):
        return self.__extract_weather_set(hour, "id", all_values)

    def weather_main(self, hour=0, all_values=False):
        return self.__extract_weather_set(hour, "main", all_values)

    def weather_description(self, hour=0, all_values=False):
        return self.__extract_weather_set(hour, "description", all_values)

    def weather_icon(self, hour=0, all_values=False):
        return self.__extract_weather_set(hour, "icon", all_values)

    def pop(self, hour=0, all_values=False):
        return self.__extract_value_set(hour, "pop", all_values)
