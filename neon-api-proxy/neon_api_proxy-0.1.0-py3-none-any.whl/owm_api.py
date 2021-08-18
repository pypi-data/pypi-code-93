# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
#
# Copyright 2008-2021 Neongecko.com Inc. | All Rights Reserved
#
# Notice of License - Duplicating this Notice of License near the start of any file containing
# a derivative of this software is a condition of license for this software.
# Friendly Licensing:
# No charge, open source royalty free use of the Neon AI software source and object is offered for
# educational users, noncommercial enthusiasts, Public Benefit Corporations (and LLCs) and
# Social Purpose Corporations (and LLCs). Developers can contact developers@neon.ai
# For commercial licensing, distribution of derivative works or redistribution please contact licenses@neon.ai
# Distributed on an "AS IS” basis without warranties or conditions of any kind, either express or implied.
# Trademarks of Neongecko: Neon AI(TM), Neon Assist (TM), Neon Communicator(TM), Klat(TM)
# Authors: Guy Daniels, Daniel McKnight, Regina Bloomstine, Elon Gasper, Richard Leeds
#
# Specialized conversational reconveyance options from Conversation Processing Intelligence Corp.
# US Patents 2008-2021: US7424516, US20140161250, US20140177813, US8638908, US8068604, US8553852, US10530923, US10530924
# China Patent: CN102017585  -  Europe Patent: EU2156652  -  Patents Pending

import urllib.parse
from requests import Response

from neon_api_proxy.cached_api import CachedAPI
from neon_utils.logger import LOG
from neon_utils.authentication_utils import find_neon_owm_key


class OpenWeatherAPI(CachedAPI):
    """
    API for querying Open Weather Map.
    """

    def __init__(self, api_key: str = None, cache_seconds=180):
        super().__init__("open_weather_map")
        self._api_key = api_key or find_neon_owm_key()
        self.cache_timeout = cache_seconds

    def handle_query(self, **kwargs) -> dict:
        """
        Handles an incoming query and provides a response
        :param kwargs:
          'lat' - str latitude
          'lng' - str longitude
          'units' - optional string "metric" or "imperial"
        :return: dict containing `status_code`, `content`, `encoding` from URL response
        """
        lat = kwargs.get("lat")
        lng = kwargs.get("lng", kwargs.get("lon"))
        units = "metric" if kwargs.get("units") == "metric" else "imperial"

        if not all((lat, lng, units)):
            return {"status_code": -1,
                    "content": f"Missing required args in: {kwargs}",
                    "encoding": None}
        try:
            resp = self._get_api_response(lat, lng, units)
        except Exception as e:
            return {"status_code": -1,
                    "content": repr(e),
                    "encoding": None}
        if not resp.ok:
            LOG.error(f"Bad response code: {resp.status_code}")
        return {"status_code": resp.status_code,
                "content": resp.content,
                "encoding": resp.encoding}

    def _get_api_response(self, lat: str, lng: str, units: str) -> Response:
        str(float(lat))
        str(float(lng))
        assert units in ("metric", "imperial", "standard")
        query_params = {"lat": lat,
                        "lon": lng,
                        "appid": self._api_key,
                        "units": units}
        query_str = urllib.parse.urlencode(query_params)
        resp = self.get_with_cache_timeout(f"http://api.openweathermap.org/data/2.5/onecall?{query_str}",
                                           self.cache_timeout)
        return resp
