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


# Derived Class to handle alerts data API response
class OneCallApiAlerts(OneCallApi):
    def __init__(self, lat, lon, key):
        super().__init__(lat, lon, key, "current,hourly,minutely,daily")

    def __is_data_available(self, field):
        value = False
        if ("alerts" in self._rawdata) and (field in self._rawdata["alerts"][0]):
            value = True
        return value

    def __extract_value_field(self, field):
        value = "N/A"
        if self.__is_data_available(field) is True:
            value = self._rawdata["alerts"][0][field]
        logger.debug("Value for %s is: %s", field, value)
        return value

    def __extract_date_field(self, field, metrics=0):
        value = "N/A"
        if self.__is_data_available(field) is True:
            if metrics == 0:
                dt = datetime.fromtimestamp(self._rawdata["alerts"][0][field])
                value = f"{dt:%Y-%m-%d %H:%M:%S}"
            else:
                value = self._rawdata["alerts"][0][field]
        logger.debug("Value for %s is: %s", field, value)
        return value

    def raw_data_alerts(self):
        value = dict()
        if "alerts" in self._rawdata:
            value = self._rawdata["alerts"]
        return value

    def sender_name(self):
        return self.__extract_value_field("sender_name")

    def event(self):
        return self.__extract_value_field("event")

    def start_dt(self, metrics=0):
        return self.__extract_date_field("start", metrics)

    def end_dt(self, metrics=0):
        return self.__extract_date_field("end", metrics)

    def description(self):
        return self.__extract_value_field("description")

    def tags(self):
        return self.__extract_value_field("tags")
