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


# Derived Class to handle Minutely weather data API response
# Minutely holds the precipitation forecast for the next hour in a minutely basis
# Gets 61 values: current + next 60 minutes
class OneCallApiMinutely(OneCallApi):
    def __init__(self, lat, lon, key):
        super().__init__(lat, lon, key, "current,daily,hourly,alerts")

    def __is_data_available(self, minute, field):
        value = False
        if ("minutely" in self._rawdata) and (field in self._rawdata["minutely"][minute]):
            value = True
        return value

    def __extract_date_field(self, minute, field, metrics=0):
        value = "N/A"
        if self.__is_data_available(minute, field) is True:
            if metrics == 0:
                dt = datetime.fromtimestamp(self._rawdata["minutely"][minute][field])
                value = f"{dt:%Y-%m-%d %H:%M:%S}"
            else:
                value = self._rawdata["minutely"][minute][field]
        logger.debug("Value for %s is: %s", field, value)
        return value

    def __extract_value_field(self, minute, field):
        value = "N/A"
        if self.__is_data_available(minute, field) is True:
            value = self._rawdata["minutely"][minute][field]
        logger.debug("Value for %s is: %s", field, value)
        return value

    def raw_data_minutely(self):
        value = dict()
        if "minutely" in self._rawdata:
            value = self._rawdata["minutely"]
        return value

    def precipitation(self, minute=0, all_values=False):
        if minute < 0 or minute > 60:
            raise ValueError("The 'minute' argument must be within range [0, 60]")
        elif all_values is True:
            value = [0] * 61  # Initialize the 61 precipitation values
            for idx in range(61):
                value[idx] = self.__extract_value_field(idx, "precipitation")
        else:
            value = self.__extract_value_field(minute, "precipitation")
        return value

    def data_time(self, minute=0, metrics=0, all_values=False):
        if minute < 0 or minute > 60:
            raise ValueError("The 'minute' argument must be within range [0, 60]")
        elif all_values is True:
            value = [0] * 61  # Initialize the 61 data time values
            for idx in range(61):
                value[idx] = self.__extract_date_field(idx, "dt", metrics)
        else:
            value = self.__extract_date_field(minute, "dt", metrics)
        return value
