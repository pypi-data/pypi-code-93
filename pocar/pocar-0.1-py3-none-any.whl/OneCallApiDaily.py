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


# Derived Class to handle Daily weather data API response
# Daily holds the weather forecast for the next 7 days in a daily basis
# Gets 7 values: weather today + for next 7 days
class OneCallApiDaily(OneCallApi):
    def __init__(self, lat, lon, key):
        super().__init__(lat, lon, key, "current,hourly,minutely,alerts")

    def __is_data_available(self, day, field):
        value = False
        if ("daily" in self._rawdata) and (field in self._rawdata["daily"][day]):
            value = True
        return value

    def __extract_date_field(self, day, field, metrics=0):
        value = "N/A"
        if self.__is_data_available(day, field) is True:
            if metrics == 0:
                dt = datetime.fromtimestamp(self._rawdata["daily"][day][field])
                value = f"{dt:%Y-%m-%d %H:%M:%S}"
            else:
                value = self._rawdata["daily"][day][field]
        logger.debug("Value for %s is: %s", field, value)
        return value

    def __extract_date_set(self, day, field, metrics=0, all_values=False):
        if day < 0 or day > 7:
            raise ValueError("The 'day' argument must be within range [0, 7]")
        elif all_values is True:
            value = [0] * 7  # Initialize the 48 data time values
            for idx in range(7):
                value[idx] = self.__extract_date_field(idx, field, metrics)
        else:
            value = self.__extract_date_field(day, field, metrics)
        return value

    def __extract_temp_field(self, day, group, field):
        value = "N/A"
        if self.__is_data_available(day, group) is True:
            if field in self._rawdata["daily"][day][group]:
                value = self._rawdata["daily"][day][group][field]
        logger.debug("Value for %s is: %s", field, value)
        return value

    def __extract_temp_set(self, day, group, field, all_values):
        if day < 0 or day > 7:
            raise ValueError("The 'day' argument must be within range [0, 7]")
        elif all_values is True:
            value = [0] * 7  # Initialize the 7 data time values
            for idx in range(7):
                value[idx] = self.__extract_temp_field(idx, group, field)
        else:
            value = self.__extract_temp_field(day, group, field)
        return value

    def __extract_value_field(self, day, field):
        value = "N/A"
        if self.__is_data_available(day, field) is True:
            value = self._rawdata["daily"][day][field]
        logger.debug("Value for %s is: %s", field, value)
        return value

    def __extract_value_set(self, day, field, all_values):
        if day < 0 or day > 7:
            raise ValueError("The 'day' argument must be within range [0, 7]")
        elif all_values is True:
            value = [0] * 7  # Initialize the 7 data time values
            for idx in range(7):
                value[idx] = self.__extract_value_field(idx, field)
        else:
            value = self.__extract_value_field(day, field)
        return value

    def __extract_weather_field(self, day, field):
        value = "N/A"
        if ("daily" in self._rawdata) and ("weather" in self._rawdata["daily"][day]):
            if field in self._rawdata["daily"][day]["weather"][0]:
                value = self._rawdata["daily"][day]["weather"][0][field]
        logger.debug("Value for %s is: %s", field, value)
        return value

    def __extract_weather_set(self, day, field, all_values):
        if day < 0 or day > 7:
            raise ValueError("The 'hour' argument must be within range [0, 7]")
        elif all_values is True:
            value = [0] * 7  # Initialize the 7 data time values
            for idx in range(7):
                value[idx] = self.__extract_weather_field(idx, field)
        else:
            value = self.__extract_weather_field(day, field)
        return value

    def raw_data_daily(self):
        value = dict()
        if "daily" in self._rawdata:
            value = self._rawdata["daily"]
        return value

    def data_time(self, day=0, metrics=0, all_values=False):
        return self.__extract_date_set(day, "dt", metrics, all_values)

    def sunrise(self, day=0, metrics=0, all_values=False):
        return self.__extract_date_set(day, "sunrise", metrics, all_values)

    def sunset(self, day=0, metrics=0, all_values=False):
        return self.__extract_date_set(day, "sunset", metrics, all_values)

    def moonrise(self, day=0, metrics=0, all_values=False):
        return self.__extract_date_set(day, "moonrise", metrics, all_values)

    def moonset(self, day=0, metrics=0, all_values=False):
        return self.__extract_date_set(day, "moonset", metrics, all_values)

    def temp_day(self, day=0, all_values=False):
        return self.__extract_temp_set(day, "temp", "day", all_values)

    def temp_min(self, day=0, all_values=False):
        return self.__extract_temp_set(day, "temp", "min", all_values)

    def temp_max(self, day=0, all_values=False):
        return self.__extract_temp_set(day, "temp", "max", all_values)

    def temp_night(self, day=0, all_values=False):
        return self.__extract_temp_set(day, "temp", "night", all_values)

    def temp_eve(self, day=0, all_values=False):
        return self.__extract_temp_set(day, "temp", "eve", all_values)

    def temp_morn(self, day=0, all_values=False):
        return self.__extract_temp_set(day, "temp", "morn", all_values)

    def feels_like_day(self, day=0, all_values=False):
        return self.__extract_temp_set(day, "feels_like", "day", all_values)

    def feels_like_night(self, day=0, all_values=False):
        return self.__extract_temp_set(day, "feels_like", "night", all_values)

    def feels_like_eve(self, day=0, all_values=False):
        return self.__extract_temp_set(day, "feels_like", "eve", all_values)

    def feels_like_morn(self, day=0, all_values=False):
        return self.__extract_temp_set(day, "feels_like", "morn", all_values)

    def pressure(self, day=0, all_values=False):
        return self.__extract_value_set(day, "pressure", all_values)

    def humidity(self, day=0, all_values=False):
        return self.__extract_value_set(day, "humidity", all_values)

    def dew_point(self, day=0, all_values=False):
        return self.__extract_value_set(day, "dew_point", all_values)

    def wind_speed(self, day=0, all_values=False):
        return self.__extract_value_set(day, "wind_speed", all_values)

    def wind_deg(self, day=0, all_values=False):
        return self.__extract_value_set(day, "wind_deg", all_values)

    def wind_gust(self, day=0, all_values=False):
        return self.__extract_value_set(day, "wind_gust", all_values)

    def clouds(self, day=0, all_values=False):
        return self.__extract_value_set(day, "clouds", all_values)

    def pop(self, day=0, all_values=False):
        return self.__extract_value_set(day, "pop", all_values)

    def uvi(self, day=0, all_values=False):
        return self.__extract_value_set(day, "uvi", all_values)

    def weather_condition_id(self, day=0, all_values=False):
        return self.__extract_weather_set(day, "id", all_values)

    def weather_condition_main(self, day=0, all_values=False):
        return self.__extract_weather_set(day, "main", all_values)

    def weather_condition_description(self, day=0, all_values=False):
        return self.__extract_weather_set(day, "description", all_values)

    def weather_condition_icon(self, day=0, all_values=False):
        return self.__extract_weather_set(day, "icon", all_values)
