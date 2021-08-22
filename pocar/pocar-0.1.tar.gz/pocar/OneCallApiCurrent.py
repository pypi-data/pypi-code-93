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


# Derived Class to handle Current weather data API response
class OneCallApiCurrent(OneCallApi):
    def __init__(self, lat, lon, key):
        super().__init__(lat, lon, key, "minutely,daily,hourly,alerts")

    def __is_data_available(self, field):
        value = False
        if ("current" in self._rawdata) and (field in self._rawdata["current"]):
            value = True
        return value

    def __extract_date_field(self, field, metrics=0):
        value = "N/A"
        if self.__is_data_available(field) is True:
            if metrics == 0:
                dt = datetime.fromtimestamp(self._rawdata["current"][field])
                value = f"{dt:%Y-%m-%d %H:%M:%S}"
            else:
                value = self._rawdata["current"][field]
        logger.debug("Value for %s is: %s", field, value)
        return value

    def __extract_value_field(self, field):
        value = "N/A"
        if self.__is_data_available(field) is True:
            value = self._rawdata["current"][field]
        logger.debug("Value for %s is: %s", field, value)
        return value

    def __extract_weather_field(self, field):
        value = "N/A"
        if self.__is_data_available("weather") is True:
            if field in self._rawdata["current"]["weather"][0]:
                value = self._rawdata["current"]["weather"][0][field]
        logger.debug("Value for %s is: %s", field, value)
        return value

    def raw_data_current(self):
        value = dict()
        if "current" in self._rawdata:
            value = self._rawdata["current"]
        return value

    # Get Current time, Unix, UTC
    # metrics defaults to 0: date in human readable format
    # any other value, date is represented as UNIX seconds
    def data_time(self, metrics=0):
        return self.__extract_date_field("dt", metrics)

    # Get Sunrise time, Unix, UTC
    def sunrise(self, metrics=0):
        return self.__extract_date_field("sunrise", metrics)

    # Get Sunset time, Unix, UTC
    def sunset(self, metrics=0):
        return self.__extract_date_field("sunset", metrics)

    # Get Current Temperature
    def temperature(self):
        return self.__extract_value_field("temp")

    # Get Current Temperature feel
    def temperature_feels_like(self):
        return self.__extract_value_field("feels_like")

    # Get Current Atmospheric pressure on the sea level, hPa
    def pressure(self):
        return self.__extract_value_field("pressure")

    # Get Current Humidity, %
    def humidity(self):
        return self.__extract_value_field("humidity")

    # Get Current Atmospheric temperature
    def dew_point(self):
        return self.__extract_value_field("dew_point")

    # Get Current Cloudiness, %
    def clouds(self):
        return self.__extract_value_field("clouds")

    # Get Current UV index
    def uvi(self):
        return self.__extract_value_field("uvi")

    # Get Current Average visibility, metres
    def visibility(self):
        return self.__extract_value_field("visibility")

    # Get Current Wind speed (m/s)
    def wind_speed(self):
        return self.__extract_value_field("wind_speed")

    # Get Current Wind gust (where available)
    def wind_gust(self):
        return self.__extract_value_field("wind_gust")

    # Get Current Wind direction, degrees (meteorological)
    def wind_deg(self):
        return self.__extract_value_field("wind_deg")

    # Get Current Rain volume for last hour, mm (where available)
    def rain_volume(self):
        value = "N/A"
        if self.__is_data_available("rain") is True:
            if "1h" in self._rawdata["current"]["rain"]:
                value = self._rawdata["current"]["rain"]["1h"]
        return value

    # Get Current Snow volume for last hour, mm (where available)
    def snow_volume(self):
        value = "N/A"
        if self.__is_data_available("snow") is True:
            if "1h" in self._rawdata["current"]["snow"]:
                value = self._rawdata["current"]["snow"]["1h"]
        return value

    # Get Current Weather condition id
    def weather_condition_id(self):
        return self.__extract_weather_field("id")

    # Get Group of weather parameters (Rain, Snow, Extreme etc.)
    def weather_condition_main(self):
        return self.__extract_weather_field("main")

    # Get Weather condition within the group (full list of weather conditions)
    def weather_condition_description(self):
        return self.__extract_weather_field("description")

    # Get Weather icon id. How to get icons
    #  http://openweathermap.org/img/wn/<icon_id>@2x.png
    def weather_condition_icon(self):
        return self.__extract_weather_field("icon")
