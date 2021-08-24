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
from neon_api_proxy.cached_api import CachedAPI
# from neon_utils.log_utils import LOG
from neon_utils.authentication_utils import find_neon_alpha_vantage_key


class QueryUrl(Enum):
    def __str__(self):
        return self.value
    SYMBOL = "https://www.alphavantage.co/query?function=SYMBOL_SEARCH"  # keywords=, apikey=
    QUOTE = "https://www.alphavantage.co/query?function=GLOBAL_QUOTE"  # symbol=, apikey=


class AlphaVantageAPI(CachedAPI):
    """
    API for querying Alpha Vantage.
    """

    def __init__(self, api_key: str = None):
        super().__init__("alpha_vantage")
        self._api_key = api_key or find_neon_alpha_vantage_key()

    def _search_symbol(self, query: str) -> dict:
        if not query:
            raise ValueError(f"Query is None")
        elif not isinstance(query, str):
            raise TypeError(f"Query is not a str: {query} ({type(query)})")
        query_params = {"keywords": query,
                        "apikey": self._api_key}
        query_str = urllib.parse.urlencode(query_params)
        resp = self.get_with_cache_timeout(f"{QueryUrl.SYMBOL}&{query_str}")
        return {"status_code": resp.status_code,
                "content": resp.content,
                "encoding": resp.encoding}

    def _get_quote(self, symbol: str):
        if not symbol:
            raise ValueError(f"symbol is None")
        elif not isinstance(symbol, str):
            raise TypeError(f"symbol is not a str: {symbol} ({type(symbol)})")
        query_params = {"symbol": symbol,
                        "apikey": self._api_key}
        query_str = urllib.parse.urlencode(query_params)
        resp = self.get_with_cache_timeout(f"{QueryUrl.QUOTE}&{query_str}", 180)
        return {"status_code": resp.status_code,
                "content": resp.content,
                "encoding": resp.encoding}

    def handle_query(self, **kwargs) -> dict:
        """
        Handles an incoming query and provides a response
        :param kwargs:
          'symbol' - optional string stock symbol to query
          'company' - optional string company name to query
          'api' - optional string 'symbol' or 'quote'
        :return: dict containing stock data from URL response
        """
        symbol = kwargs.get('symbol')
        company = kwargs.get('company', kwargs.get('keywords'))
        search_term = symbol or company
        if not search_term:
            return {"status_code": -1,
                    "content": f"No search term provided",
                    "encoding": None}

        api = kwargs.get("api")
        if not api:
            query_type = QueryUrl.QUOTE
        elif api == "symbol":
            query_type = QueryUrl.SYMBOL
        elif api == "quote":
            query_type = QueryUrl.QUOTE
        else:
            return {"status_code": -1,
                    "content": f"Unknown api requested: {api}",
                    "encoding": None}

        try:
            if query_type == QueryUrl.SYMBOL:
                return self._search_symbol(search_term)
            elif query_type == QueryUrl.QUOTE:
                if not symbol:
                    return {"status_code": -1,
                            "content": f"No symbol provided",
                            "encoding": None}
                else:
                    return self._get_quote(symbol)
        except Exception as e:
            return {"status_code": -1,
                    "content": repr(e),
                    "encoding": None}
