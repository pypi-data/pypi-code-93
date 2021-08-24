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

from enum import Enum
from neon_utils.log_utils import LOG
from neon_utils.authentication_utils import find_neon_wolfram_key
from neon_api_proxy.cached_api import CachedAPI


class QueryUrl(Enum):
    def __str__(self):
        return self.value
    SIMPLE = "http://api.wolframalpha.com/v2/simple"
    SHORT = "http://api.wolframalpha.com/v2/result"
    SPOKEN = "http://api.wolframalpha.com/v2/spoken"
    FULL = "http://api.wolframalpha.com/v2/query"
    RECOGNIZE = "http://www.wolframalpha.com/queryrecognizer/query.jsp"
    CONVERSATION = "http://api.wolframalpha.com/v1/conversation.jsp"


class WolframAPI(CachedAPI):
    """
    API for querying Wolfram|Alpha.
    """

    def __init__(self, api_key: str = None):
        super().__init__("wolfram")
        self._api_key = api_key or find_neon_wolfram_key()
        self.session.allowable_codes = (200, 501)

    def _build_query_url(self, query_type: QueryUrl, query_arg: str) -> str:
        """
        Constructs a valid URL for the given query_type and query_arg
        :param query_type: QueryUrl to query
        :param query_arg: string args relating to question
        :return: valid URL to query for a response
        """
        if not query_type:
            raise ValueError(f"query_type not defined!")
        if not query_arg:
            raise ValueError(f"query_url not defined!")
        if not isinstance(query_type, QueryUrl):
            raise TypeError(f"Not a QueryUrl: {query_arg}")
        if not isinstance(query_arg, str):
            raise TypeError(f"Not a string: {query_arg}")
        if query_type == QueryUrl.RECOGNIZE:
            query_arg = f"{query_arg}&mode=Default"
        return f"{query_type}?appid={self._api_key}&{query_arg}"

    @staticmethod
    def _build_query_string(**kwargs) -> str:
        """
        Constructs a valid query string with the given arguments
        :param kwargs:
          'query' - string query to ask Wolfram|Alpha
          'units' - optional string "metric" or "nonmetric"
          'lat'+'lng' optional float or string lat/lng (separate keys)
          'ip' optional string origin IP Address for geolocation
        :return: URL encoded query string used to build a request URL
        """
        if not kwargs.get("query"):
            raise ValueError(f"No query in request: {kwargs}")
        query_params = dict()
        query_params['i'] = kwargs.get("query")
        query_params['units'] = kwargs.get("units") if kwargs.get("units") == "metric" else "nonmetric"
        lat = kwargs.get("lat")
        lng = kwargs.get("lng")
        if kwargs.get("latlong"):
            query_params["latlong"] = kwargs.get("latlong")
        elif lat and lng:
            query_params["latlong"] = f"{lat},{lng}"
        else:
            query_params["ip"] = kwargs.get("ip")

        query_params = {k: v for k, v in query_params.items() if v}
        query_str = urllib.parse.urlencode(query_params)
        return query_str

    def handle_query(self, **kwargs) -> dict:
        """
        Handles an incoming query and provides a response
        :param kwargs:
          'query' - string query to ask Wolfram|Alpha
          'api' - string api to query (simple, short, spoken, full, recognize, conversation)
          'units' - optional string "metric" or "nonmetric"
          'latlong' - optional string lat/lng
          'lat'+'lng' - optional float or string lat/lng (separate keys)
          'ip' - optional string origin IP Address for geolocation
        :return: dict containing `status_code`, `content`, `encoding` from URL response
        """
        api = kwargs.get("api")
        if not api:
            query_type = QueryUrl.SHORT
        elif api == "simple":
            query_type = QueryUrl.SIMPLE
        elif api == "short":
            query_type = QueryUrl.SHORT
        elif api == "spoken":
            query_type = QueryUrl.SPOKEN
        elif api == "full":
            query_type = QueryUrl.FULL
        elif api == "recognize":
            query_type = QueryUrl.RECOGNIZE
        elif api == "conversation":
            query_type = QueryUrl.CONVERSATION
        else:
            return {"status_code": -1,
                    "content": f"Unknown api requested: {api}",
                    "encoding": None}

        try:
            query_str = self._build_query_string(**kwargs)
            return self._query_api(self._build_query_url(query_type, query_str))
        except Exception as e:
            return {"status_code": -1,
                    "content": repr(e),
                    "encoding": None}

    def _query_api(self, query: str) -> dict:
        """
        Queries the Wolfram|Alpha API and returns a dict with the status, content, and encoding
        :param query: URL to query
        :return: dict response containing: `status_code`, `content`, and `encoding`
        """
        result = self.get_with_cache_timeout(query)
        if not result.ok:
            # 501 = Wolfram couldn't understand
            # 403 = Invalid API Key Provided
            LOG.warning(f"API Query error ({result.status_code}): {query}")
        return {"status_code": result.status_code,
                "content": result.content,
                "encoding": result.encoding}
