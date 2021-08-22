#!/usr/bin/env python3

import json
import logging
import requests
import time

# Uncomment this line to suppress warning message due to:
#    InsecureRequestWarning: Unverified HTTPS request is being made.
#    Adding certificate verification is strongly advised.
#    See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
# We get this warning because an HTTP GET request is made with SSL verification disabled
requests.packages.urllib3.disable_warnings()

# Set local logger to the root logger, to inherit root settings
logger = logging.getLogger(__name__)


# Base Class to handle OneCallApi response from OpenWeatherMap
class OneCallApi:
    def __init__(self, lat, lon, key, exc=""):
        self.lat = lat
        self.lon = lon
        self.key = key
        self.exc = exc
        self._rawdata = dict()
        self._timestamp = 0
        self.__url = (
            f"https://api.openweathermap.org/data/2.5/onecall?lat={self._lat}&lon={self._lon}"
            f"&exclude={self._exc}&units=metric&appid={self._key}"
        )

    @property
    def lat(self):
        logger.debug("Get method for 'lat' attribute")
        return self._lat

    @lat.setter
    def lat(self, lat):
        logger.debug("Set method for 'lat' attribute")
        if lat < -90.0 or lat > 90.0:
            raise ValueError("The 'lat' argument must be within range [-90, 90]")
        else:
            self._lat = lat
            logger.debug("Set 'lat' value to: %s", self._lat)

    @property
    def lon(self):
        logger.debug("Get method for 'lon' attribute")
        return self._lon

    @lon.setter
    def lon(self, lon):
        logger.debug("Set method for 'lon' attribute")
        if lon < -180.0 or lon > 180.0:
            raise ValueError("The 'lon' argument must be within range [-180, 180]")
        else:
            self._lon = lon
            logger.debug("Set 'lon' value to: %s", self._lon)

    @property
    def key(self):
        logger.debug("Get method for 'key' attribute")
        return self._key

    @key.setter
    def key(self, key):
        logger.debug("Set method for 'key' attribute")
        # The 128-bit (16-byte) OpenWeatherMap hash key is represented as a sequence of 32 hexadecimal digits
        try:
            int(key, 16)
        except ValueError:
            logger.error("The 'key' argument must be an hash value of 32 hexadecimal digits")
            raise  # raise error for traceback access

        if len(key) != 32:
            raise ValueError("The 'key' argument must have a size of 32")
        else:
            self._key = key
            logger.debug("Set 'key' value to: %s", self._key)

    @property
    def exc(self):
        logger.debug("Get method for 'exc' attribute")
        return self._exc

    @exc.setter
    def exc(self, exc):
        logger.debug("Set method for 'exc' attribute")
        if len(exc) == 0:
            # the exclusion string can be empty, meaning that none of the OneCallAPi response are excluded
            # nothing to be done
            self._exc = exc
        elif any(True for char in exc if char in '@^! #%$&)(+*-="'):
            # the exclusion shall be a comma-delimited string (without spaces).
            # Allowed values are: current, minutely, hourly, daily and alerts
            raise ValueError("The 'exc' argument must be a comma-delimited string (without spaces)")
        else:
            # the exclusion shall contain specific words
            specWordList = ["current", "minutely", "hourly", "daily", "alerts"]
            excWordList = exc.split(",")
            for excWord in excWordList:
                if excWord in specWordList:
                    logger.debug("The 'exc' argument contains word: %s", excWord)
                else:
                    logger.error("The 'exc' argument contains an invalid word: %s", excWord)
                    raise ValueError("The 'exc' argument must specific words: (current, minutely, hourly, daily, alerts)")
            self._exc = exc
        logger.debug("Set 'exc' value to: %s", self._exc)

    # Gets the configuration used to access OpenWeatherMap for OneCallApi.
    def config(self):
        conf_dict = dict(
            {
                "lat": self._lat,
                "lon": self._lon,
                "key": self._key,
                "exc": self._exc,
                "url": self.__url,
            }
        )
        logger.debug("Configuration to access OpenWeatherMap for OneCallApi: ")
        logger.debug("   Latitude       : %s", self._lat)
        logger.debug("   Longitude      : %s", self._lon)
        logger.debug("   Excluded parts : %s", self._exc)
        logger.debug("   API Key        : %s", self._key)
        logger.debug("   API url        : %s", self.__url)
        return conf_dict

    # Get OpenWeatherMap raw data from OneCallApi response. (full response)
    def raw_data(self):
        return self._rawdata

    # Get OpenWeatherMap data from OneCallApi
    # Data is stored as a dictionary in self._rawdata
    def __getData(self):
        is_data_updated = False
        req = requests.get(self.__url, verify=False)
        try:
            req.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            logger.warning(errh)
            # raise
        except requests.exceptions.ConnectionError as errc:
            logger.warning(errc)
            # raise
        except requests.exceptions.TimeoutError as errt:
            logger.warning(errt)
            # raise
        except requests.exceptions.RequestsException as err:
            logger.warning(err)
            # raise
        else:
            self._rawdata = req.json()
            logger.debug(
                "OneCallApi response, as json raw data:\n%s",
                json.dumps(self._rawdata, indent=2),
            )
            self._timestamp = time.time()
            logger.debug("OneCallApi response timestamp: %s", self._timestamp)
            is_data_updated = True
        return is_data_updated

    # Make an update of OpenWeatherMap data
    # Returns:
    #   True: if data successfuly updated
    #   False: if failed to update data
    def updateData(self):
        return self.__getData()

    # Get Timezone name for the requested location
    def timezone(self):
        value = ""
        if "timezone" in self._rawdata:
            value = self._rawdata["timezone"]
        return value

    # Get Timezone offset Shift in seconds of the requested location from UTC
    def timezone_offset(self):
        value = ""
        if "timezone_offset" in self._rawdata:
            value = self._rawdata["timezone_offset"]
        return value

    # Get timestamp of OpenWeatherMap data in seconds
    def timestamp(self):
        return self._timestamp
