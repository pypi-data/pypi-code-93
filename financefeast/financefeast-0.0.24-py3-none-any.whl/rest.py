import os
import logging
import requests
from enum import Enum
from functools import lru_cache
from requests.exceptions import ReadTimeout, Timeout, HTTPError
import os
from .exceptions import NotAuthorised, MissingClientId, MissingClientSecret, MissingTicker, RateLimitExceeded
from financefeast.common import Environments
from financefeast.entity import Response


os.environ['NO_PROXY'] = 'localhost'

"""
Financefeast client API library
https://financefeast.io
"""


class APIError(Exception):
    """
    Form an API error object
    error.status_code will have http status code.
    """

    def __init__(self, error, http_error=None):
        super().__init__(error['message'])
        self._error = error
        self._http_error = http_error

    @property
    def code(self):
        return self._error['code']

    @property
    def status_code(self):
        http_error = self._http_error
        if http_error is not None and hasattr(http_error, 'detail'):
            return http_error.response.status_code

    @property
    def request(self):
        if self._http_error is not None:
            return self._http_error.request

    @property
    def response(self):
        if self._http_error is not None:
            return self._http_error.response


class Rest:

    DEFAULT_LOG_LEVEL = logging.INFO

    def __init__(self, client_id:str = None, client_secret:str = None, token:str = None, logger:logging.Logger = None, environment:Environments=Environments.prod, **kwargs):
        self._client_id = client_id
        self._client_secret = client_secret
        self._token = token
        self._logger = logger
        self._kwargs = kwargs
        self._environment = environment

        if not logger:
            self._logger = logging.getLogger('ff_client')

        # set log level
        logging.basicConfig(level=self.DEFAULT_LOG_LEVEL)

        self._requests = self.RequestRateLimited(self._logger)

        self._logger.info(f"API environment set as {self._environment.name}")


    def __authorize(self):
        """
        Authorize client credentials
        :return: access token
        """

        if not self._token:
            if not self._client_id:
                self._client_id = os.environ.get('FF-CLIENT-ID')
            if not self._client_secret:
                self._client_secret = os.environ.get('FF-CLIENT-SECRET')

            if not self._client_secret and not self._token:
                raise MissingClientSecret(
                    "parameter 'client_id' must be either passed or set as an environment variable 'FF-CLIENT-ID', or pass parameter 'token' with a valid bearer token"
                )

            if not self._client_id and not self._token:
                raise MissingClientId(
                    "parameter 'client_secret' must be either passed or set as an environment variable 'FF-CLIENT-SECRET', or pass parameter 'token' with a valid bearer token"
                )

            if not self._token and self._client_id and self._client_secret:
                url = f'{self._environment.value}/oauth/login'
                self._logger.debug(f'Constructed url {url} for authorization')

                headers = {"X-FF-ID": self._client_id, "X-FF-SECRET": self._client_secret}

                r = self._requests.get(url=url, headers=headers)

                if r.access_token:
                    self._token = r.access_token
                    self._logger.debug('Found a valid access_token')

                    self._logger.info("Client successfully authorized to API using client credentials")
                    return self._token

            self._logger.warning("No client_id, client_secret or an invalid token has been submitted. Pass a valid token or supply your client credentails to authorize to the Financefeast API")
            raise NotAuthorised()

        return self._token

    def __check_authorization(self):
        """
        Check a token is valid by calling the validate endpoint
        :return:
        """
        self._logger.debug("Introspecting token")
        introspected_token_result = self.validate()

        if not introspected_token_result:
            self._token = None
            self._logger.warning(f"Token is not valid or has expired.")
            return False

        self._logger.debug("Token is valid")
        return True


    def __generate_authorization_header(self):
        return {'Authorization': f'Bearer {self._token}'}


    class RequestRateLimited():
        TIMEOUT_CONN = 1.5
        TIMEOUT_RESP = 5
        RATE_LIMIT_HEADER_LIMIT_NAME = 'x-ratelimit-limit'
        RATE_LIMIT_HEADER_REMAINING_NAME = 'x-ratelimit-remaining'
        RATE_LIMIT_HEADER_RESET_NAME = 'x-ratelimit-reset'

        def __init__(self, logger:logging.Logger = None):
            self.logger = logger
            self.session = requests.Session()
            self.rate_limit = None
            self.rate_limit_remaining = None
            self.rate_limit_reset = None

        def __parse_request_rate_limit_headers(self, request):

            try:
                self.rate_limit = request.headers[self.RATE_LIMIT_HEADER_LIMIT_NAME]
                self.logger.debug(f"Rate limit is {self.rate_limit}")
            except KeyError:
                self.logger.debug(f'No request header found for {self.RATE_LIMIT_HEADER_LIMIT_NAME}')
                self.rate_limit = None

            try:
                self.rate_limit_remaining = request.headers[self.RATE_LIMIT_HEADER_REMAINING_NAME]
                self.logger.debug(f"Rate limit remaining is {self.rate_limit_remaining}")
            except KeyError:
                self.logger.debug(f'No request header found for {self.RATE_LIMIT_HEADER_REMAINING_NAME}')
                self.rate_limit_remaining = None

            try:
                self.rate_limit_reset = request.headers[self.RATE_LIMIT_HEADER_RESET_NAME]
                self.logger.debug(f"Rate limit reset at {self.rate_limit_reset}")
            except KeyError:
                self.logger.debug(f'No request header found for {self.RATE_LIMIT_HEADER_RESET_NAME}')
                self.rate_limit_reset = None

            return

        def get(self, *args, **kwargs):

            self.logger.debug(f'Calling url {kwargs.get("url")}')

            try:
                r = requests.get(*args, timeout=(self.TIMEOUT_CONN, self.TIMEOUT_RESP), **kwargs)
            except (ReadTimeout, Timeout) as e:
                # timeout error
                raise
            except HTTPError as e:
                if 'detail' in r.text:
                    error = r.json()
                    raise APIError(error=error, http_error=e)
                else:
                    raise

            if r.status_code == 403:
                raise NotAuthorised(r.json())
            if r.status_code == 404:
                raise MissingTicker(r.json())
            if r.status_code == 429:
                raise RateLimitExceeded(r.json())

            if r.text:
                try:
                    r = r.json()
                except Exception as e:
                    r = {}
                return Response(r)

            return None

    @property
    def token(self):
        return self._token

    @property
    def request(self):
        return self._requests

    """
        Endpoint methods below
    """

    def validate(self):
        """
        Call oauth/validate endpoint to validate token
        :return: str
        """

        """
        Endpoint requires a valid token. Authorize client_id and client_secret first if token not passed
        """
        self.__authorize()

        url = url = f'{self._environment.value}/oauth/validate'
        headers = self.__generate_authorization_header()

        return self._requests.get(url=url, headers=headers)

    def alive(self):
        """
        Call health/alive endpoint to get health of the API
        :return: str
        """
        url = url = f'{self._environment.value}/health/alive'

        return self._requests.get(url=url)

    def usage(self,date_from:str=None, date_to:str=None):
        """
        Get account usage by endpoint and count by day
        :param date_from:
        :param date_to:
        :return:
        """

        """
        Endpoint requires a valid token. Authorize client_id and client_secret first if token not passed
        """
        self.__authorize()

        url = url = f'{self._environment.value}/account/usage'
        headers = self.__generate_authorization_header()

        # build query parameters for endpoint
        query = {}

        if date_from:
            query.update({'date_from' : date_from})

        if date_to:
            query.update({'date_to' : date_to})

        return self._requests.get(url=url, headers=headers, params=query)

    def tickers(self, exchange:str=None):
        """
        Call info/ticker endpoint to get a list of supported tickers
        :param exchange: Exchange to limit tickers to
        :return: list
        """
        url = url = f'{self._environment.value}/info/ticker'

        # build query parameters for endpoint
        query = {}

        if exchange:
            query.update({'exchange': exchange})

        return self._requests.get(url=url, params=query)

    def tickers_search(self, search_str:str, exchange:str=None):
        """
        Call info/ticker_search endpoint to get a list of supported tickers matching search string
        :param search_str: A search string of a ticker symbol, company name or uuid4
        :param exchange: Exchange to limit tickers to
        :return: list
        """
        url = url = f'{self._environment.value}/info/ticker/{search_str}'

        # build query parameters for endpoint
        query = {}

        if exchange:
            query.update({'exchange': exchange})

        return self._requests.get(url=url, params=query)

    def exchanges(self):
        """
        Call info/exchange endpoint to get a list of supported exchanges
        :return: list
        """
        url = url = f'{self._environment.value}/info/exchange'

        return self._requests.get(url=url)

    def social_sentiment(self, ticker:str, date_from:str=None, date_to:str=None, platform:str=None, exchange:str='nzx'):
        """
        Call the alternate/social-sentiment endpoint to return social media sentiment
        :param ticker: ticker to search data for, eg air.nz
        :param date_from: in format YYYY-MM-DD
        :param date_to: in format YYYY-MM-DD
        :param platform: social media platform, eg twitter
        :param exchange: exchange ticker is in
        :return:
        """

        """
        Endpoint requires a valid token. Authorize client_id and client_secret first if token not passed
        """
        self.__authorize()

        url = url = f'{self._environment.value}/alternate/social-sentiment'
        headers = self.__generate_authorization_header()

        # check required parameters
        if not ticker:
            raise MissingTicker(
                "parameter `ticker` must be either passed"
            )

        # build query parameters for endpoint
        query = {'ticker' : ticker}

        if date_from:
            query.update({'date_from' : date_from})

        if date_to:
            query.update({'date_to' : date_to})

        if exchange:
            query.update({'exchange' : exchange})

        if platform:
            query.update({'platform' : platform})

        return self._requests.get(url=url, headers=headers, params=query)

    def cpi(self, date_from:str=None, date_to:str=None, year:str=None):
        """
        Call alternate/cpi endpoint to get consumer price index data
        :param date_from: in format YYYY-MM-DD
        :param date_to: in format YYYY-MM-DD
        :param year: year to search records for in format YYYY, eg 2020
        :return:
        """

        """
        Endpoint requires a valid token. Authorize client_id and client_secret first if token not passed
        """
        self.__authorize()

        url = url = f'{self._environment.value}/alternate/cpi'
        headers = self.__generate_authorization_header()

        # check required parameters
        # None

        # build query parameters for endpoint
        query = {}

        if date_from:
            query.update({'date_from' : date_from})

        if date_to:
            query.update({'date_to' : date_to})

        if year:
            query.update({'year' : year})

        return self._requests.get(url=url, headers=headers, params=query)



    def eod(self, ticker:str, date_from:str=None, date_to:str=None, exchange:str='nzx', interval:str='1d'):
        """
        Call data/eod endpoint to get eod of day data
        :param ticker: ticker to search data for, eg air.nz
        :param date_from: in format YYYY-MM-DD
        :param date_to: in format YYYY-MM-DD
        :param exchange: exhange ticker is in
        :param interval: data time interval, eg 1d
        :return:
        """

        """
        Endpoint requires a valid token. Authorize client_id and client_secret first if token not passed
        """
        self.__authorize()

        url = url = f'{self._environment.value}/data/eod'
        headers = self.__generate_authorization_header()

        # check required parameters
        if not ticker:
            raise MissingTicker(
                "parameter `ticker` must be either passed"
            )

        # build query parameters for endpoint
        query = {'ticker' : ticker}

        if date_from:
            query.update({'date_from' : date_from})

        if date_to:
            query.update({'date_to' : date_to})

        if exchange:
            query.update({'exchange' : exchange})

        if interval:
            query.update({'interval' : interval})

        return self._requests.get(url=url, headers=headers, params=query)


    def intraday(self, ticker:str, datetime_from:str=None, datetime_to:str=None, exchange:str='nzx', interval:str='1h'):
        """
        Call data/eod endpoint to get eod of day data
        :param ticker: ticker to search data for, eg air.nz
        :param datetime_from: in format YYYY-MM-DD 00:00:00
        :param datetime_to: in format YYYY-MM-DD 00:00:00
        :param exchange: exchange ticker is in
        :param interval: data time interval, eg 1h
        :return:
        """

        """
        Endpoint requires a valid token. Authorize client_id and client_secret first if token not passed
        """
        self.__authorize()

        url = url = f'{self._environment.value}/data/intraday'
        headers = self.__generate_authorization_header()

        # check required parameters
        if not ticker:
            raise MissingTicker(
                "parameter `ticker` must be either passed"
            )

        # build query parameters for endpoint
        query = {'ticker' : ticker}

        if datetime_from:
            query.update({'date_from' : datetime_from})

        if datetime_to:
            query.update({'date_to' : datetime_to})

        if exchange:
            query.update({'exchange' : exchange})

        if interval:
            query.update({'interval' : interval})

        return self._requests.get(url=url, headers=headers, params=query)


    def last(self, ticker:str, exchange:str='nzx'):
        """
        Call data/last endpoint to get last data record for ticker
        :param ticker: ticker to search data for, eg air.nz
        :param exchange: exchange ticker is in
        :return:
        """

        """
        Endpoint requires a valid token. Authorize client_id and client_secret first if token not passed
        """
        self.__authorize()

        url = url = f'{self._environment.value}/data/last'
        headers = self.__generate_authorization_header()

        # check required parameters
        if not ticker:
            raise MissingTicker(
                "parameter `ticker` must be either passed"
            )

        # build query parameters for endpoint
        query = {'ticker' : ticker}

        if exchange:
            query.update({'exchange' : exchange})

        return self._requests.get(url=url, headers=headers, params=query)

    def sma(self, ticker:str, datetime_from:str=None, datetime_to:str=None, exchange:str='nzx', interval:str='1h', window:list = [30]):
        """
        Call ta/sm-ma endpoint to get simple moving average data
        :param ticker: ticker to search data for, eg air.nz
        :param datetime_from: in format YYYY-MM-DD 00:00:00
        :param datetime_to: in format YYYY-MM-DD 00:00:00
        :param exchange: exchange ticker is in
        :param interval: data time interval, eg 1h
        :param window: a list of moving average windows to calculate, default is [30]
        :return:
        """

        """
        Endpoint requires a valid token. Authorize client_id and client_secret first if token not passed
        """
        self.__authorize()

        url = url = f'{self._environment.value}/ta/sm-ma'
        headers = self.__generate_authorization_header()

        # check required parameters
        if not ticker:
            raise MissingTicker(
                "parameter `ticker` must be either passed"
            )

        # build query parameters for endpoint
        query = {'ticker' : ticker}

        if datetime_from:
            query.update({'date_from' : datetime_from})

        if datetime_to:
            query.update({'date_to' : datetime_to})

        if exchange:
            query.update({'exchange' : exchange})

        if interval:
            query.update({'interval' : interval})

        if window:
            query.update({'window': window})

        return self._requests.get(url=url, headers=headers, params=query)


    def ema(self, ticker:str, datetime_from:str=None, datetime_to:str=None, exchange:str='nzx', interval:str='1h', window:list = [30]):
        """
        Call ta/sm-ma endpoint to get exponential moving average data
        :param ticker: ticker to search data for, eg air.nz
        :param datetime_from: in format YYYY-MM-DD 00:00:00
        :param datetime_to: in format YYYY-MM-DD 00:00:00
        :param exchange: exchange ticker is in
        :param interval: data time interval, eg 1h
        :param window: a list of moving average windows to calculate, default is [30]
        :return:
        """

        """
        Endpoint requires a valid token. Authorize client_id and client_secret first if token not passed
        """
        self.__authorize()

        url = url = f'{self._environment.value}/ta/ep-ma'
        headers = self.__generate_authorization_header()

        # check required parameters
        if not ticker:
            raise MissingTicker(
                "parameter `ticker` must be either passed"
            )

        # build query parameters for endpoint
        query = {'ticker' : ticker}

        if datetime_from:
            query.update({'date_from' : datetime_from})

        if datetime_to:
            query.update({'date_to' : datetime_to})

        if exchange:
            query.update({'exchange' : exchange})

        if interval:
            query.update({'interval' : interval})

        if window:
            query.update({'window': window})

        return self._requests.get(url=url, headers=headers, params=query)


    def macd(self, ticker:str, datetime_from:str=None, datetime_to:str=None, exchange:str='nzx', interval:str='1h'):
        """
        Call ta/macd endpoint to get moving average convergence divergence data
        :param ticker: ticker to search data for, eg air.nz
        :param datetime_from: in format YYYY-MM-DD 00:00:00
        :param datetime_to: in format YYYY-MM-DD 00:00:00
        :param exchange: exchange ticker is in
        :param interval: data time interval, eg 1h
        :return:
        """

        """
        Endpoint requires a valid token. Authorize client_id and client_secret first if token not passed
        """
        self.__authorize()

        url = url = f'{self._environment.value}/ta/macd'
        headers = self.__generate_authorization_header()

        # check required parameters
        if not ticker:
            raise MissingTicker(
                "parameter `ticker` must be either passed"
            )

        # build query parameters for endpoint
        query = {'ticker' : ticker}

        if datetime_from:
            query.update({'date_from' : datetime_from})

        if datetime_to:
            query.update({'date_to' : datetime_to})

        if exchange:
            query.update({'exchange' : exchange})

        if interval:
            query.update({'interval' : interval})

        return self._requests.get(url=url, headers=headers, params=query)


    def rsi(self, ticker:str, datetime_from:str=None, datetime_to:str=None, exchange:str='nzx', interval:str='1h', window:int = 14):
        """
        Call ta/rsi endpoint to get relative strength indicator data
        :param ticker: ticker to search data for, eg air.nz
        :param datetime_from: in format YYYY-MM-DD 00:00:00
        :param datetime_to: in format YYYY-MM-DD 00:00:00
        :param exchange: exchange ticker is in
        :param interval: data time interval, eg 1h
        :param window: a list of moving average windows to calculate, default is [30]
        :return:
        """

        """
        Endpoint requires a valid token. Authorize client_id and client_secret first if token not passed
        """
        self.__authorize()

        url = url = f'{self._environment.value}/ta/rsi'
        headers = self.__generate_authorization_header()

        # check required parameters
        if not ticker:
            raise MissingTicker(
                "parameter `ticker` must be either passed"
            )

        # build query parameters for endpoint
        query = {'ticker' : ticker}

        if datetime_from:
            query.update({'date_from' : datetime_from})

        if datetime_to:
            query.update({'date_to' : datetime_to})

        if exchange:
            query.update({'exchange' : exchange})

        if interval:
            query.update({'interval' : interval})

        if window:
            query.update({'window': window})

        return self._requests.get(url=url, headers=headers, params=query)


    def adx(self, ticker:str, datetime_from:str=None, datetime_to:str=None, exchange:str='nzx', interval:str='1h', window:int = 5, window_adx:int = 15):
        """
        Call ta/adx endpoint to get average directional index data
        :param ticker: ticker to search data for, eg air.nz
        :param datetime_from: in format YYYY-MM-DD 00:00:00
        :param datetime_to: in format YYYY-MM-DD 00:00:00
        :param exchange: exchange ticker is in
        :param interval: data time interval, eg 1h
        :param window: first adx sliding window lookback
        :param window_adx: last adx sliding window lookback
        :return:
        """

        """
        Endpoint requires a valid token. Authorize client_id and client_secret first if token not passed
        """
        self.__authorize()

        url = url = f'{self._environment.value}/ta/adx'
        headers = self.__generate_authorization_header()

        # check required parameters
        if not ticker:
            raise MissingTicker(
                "parameter `ticker` must be either passed"
            )

        # build query parameters for endpoint
        query = {'ticker' : ticker}

        if datetime_from:
            query.update({'date_from' : datetime_from})

        if datetime_to:
            query.update({'date_to' : datetime_to})

        if exchange:
            query.update({'exchange' : exchange})

        if interval:
            query.update({'interval' : interval})

        if window:
            query.update({'window': window})

        if window_adx:
            query.update({'window_adx': window_adx})

        return self._requests.get(url=url, headers=headers, params=query)


    def bollinger(self, ticker:str, datetime_from:str=None, datetime_to:str=None, exchange:str='nzx', interval:str='1h', window:int = 20):
        """
        Call ta/bollinger endpoint to get bollinger band data
        :param ticker: ticker to search data for, eg air.nz
        :param datetime_from: in format YYYY-MM-DD 00:00:00
        :param datetime_to: in format YYYY-MM-DD 00:00:00
        :param exchange: exchange ticker is in
        :param interval: data time interval, eg 1h
        :param window: a list of moving average windows to calculate, default is [30]
        :return:
        """

        """
        Endpoint requires a valid token. Authorize client_id and client_secret first if token not passed
        """
        self.__authorize()

        url = url = f'{self._environment.value}/ta/bollinger'
        headers = self.__generate_authorization_header()

        # check required parameters
        if not ticker:
            raise MissingTicker(
                "parameter `ticker` must be either passed"
            )

        # build query parameters for endpoint
        query = {'ticker' : ticker}

        if datetime_from:
            query.update({'date_from' : datetime_from})

        if datetime_to:
            query.update({'date_to' : datetime_to})

        if exchange:
            query.update({'exchange' : exchange})

        if interval:
            query.update({'interval' : interval})

        if window:
            query.update({'window': window})

        return self._requests.get(url=url, headers=headers, params=query)


    def stochastic(self, ticker:str, datetime_from:str=None, datetime_to:str=None, exchange:str='nzx', interval:str='1h', window:int = 14, window_sma:int = 3):
        """
        Call ta/stochastic endpoint to get stochastic oscillator data
        :param ticker: ticker to search data for, eg air.nz
        :param datetime_from: in format YYYY-MM-DD 00:00:00
        :param datetime_to: in format YYYY-MM-DD 00:00:00
        :param exchange: exchange ticker is in
        :param interval: data time interval, eg 1h
        :param window: window lookback
        :param window_sma: simple moving average window
        :return:
        """

        """
        Endpoint requires a valid token. Authorize client_id and client_secret first if token not passed
        """
        self.__authorize()

        url = url = f'{self._environment.value}/ta/stochastic'
        headers = self.__generate_authorization_header()

        # check required parameters
        if not ticker:
            raise MissingTicker(
                "parameter `ticker` must be either passed"
            )

        # build query parameters for endpoint
        query = {'ticker' : ticker}

        if datetime_from:
            query.update({'date_from' : datetime_from})

        if datetime_to:
            query.update({'date_to' : datetime_to})

        if exchange:
            query.update({'exchange' : exchange})

        if interval:
            query.update({'interval' : interval})

        if window:
            query.update({'window': window})

        if window_sma:
            query.update({'window_sma': window_sma})

        return self._requests.get(url=url, headers=headers, params=query)


    def cashflow(self, ticker:str, date_from:str=None, date_to:str=None, year:str=None, exchange:str='nzx'):
        """
        Call financial/cashflow endpoint to get cashflow financial data
        :param ticker: ticker to search data for, eg air.nz
        :param date_from: in format YYYY-MM-DD
        :param date_to: in format YYYY-MM-DD
        :param exchange: exchange ticker is in
        :param year: year to search records for in format YYYY, eg 2020
        :return:
        """

        """
        Endpoint requires a valid token. Authorize client_id and client_secret first if token not passed
        """
        self.__authorize()

        url = url = f'{self._environment.value}/financial/cashflow'
        headers = self.__generate_authorization_header()

        # check required parameters
        if not ticker:
            raise MissingTicker(
                "parameter `ticker` must be either passed"
            )

        # build query parameters for endpoint
        query = {'ticker' : ticker}

        if date_from:
            query.update({'date_from' : date_from})

        if date_to:
            query.update({'date_to' : date_to})

        if exchange:
            query.update({'exchange' : exchange})

        if year:
            query.update({'year' : year})

        return self._requests.get(url=url, headers=headers, params=query)


    def income(self, ticker:str, date_from:str=None, date_to:str=None, year:str=None, exchange:str='nzx'):
        """
        Call financial/income endpoint to get income financial data
        :param ticker: ticker to search data for, eg air.nz
        :param date_from: in format YYYY-MM-DD
        :param date_to: in format YYYY-MM-DD
        :param exchange: exchange ticker is in
        :param year: year to search records for in format YYYY, eg 2020
        :return:
        """

        """
        Endpoint requires a valid token. Authorize client_id and client_secret first if token not passed
        """
        self.__authorize()

        url = url = f'{self._environment.value}/financial/income'
        headers = self.__generate_authorization_header()

        # check required parameters
        if not ticker:
            raise MissingTicker(
                "parameter `ticker` must be either passed"
            )

        # build query parameters for endpoint
        query = {'ticker' : ticker}

        if date_from:
            query.update({'date_from' : date_from})

        if date_to:
            query.update({'date_to' : date_to})

        if exchange:
            query.update({'exchange' : exchange})

        if year:
            query.update({'year' : year})

        return self._requests.get(url=url, headers=headers, params=query)



    def balance(self, ticker:str, date_from:str=None, date_to:str=None, year:str=None, exchange:str='nzx'):
        """
        Call financial/balance endpoint to get balance sheet financial data
        :param ticker: ticker to search data for, eg air.nz
        :param date_from: in format YYYY-MM-DD
        :param date_to: in format YYYY-MM-DD
        :param exchange: exchange ticker is in
        :param year: year to search records for in format YYYY, eg 2020
        :return:
        """

        """
        Endpoint requires a valid token. Authorize client_id and client_secret first if token not passed
        """
        self.__authorize()

        url = url = f'{self._environment.value}/financial/balance'
        headers = self.__generate_authorization_header()

        # check required parameters
        if not ticker:
            raise MissingTicker(
                "parameter `ticker` must be either passed"
            )

        # build query parameters for endpoint
        query = {'ticker' : ticker}

        if date_from:
            query.update({'date_from' : date_from})

        if date_to:
            query.update({'date_to' : date_to})

        if exchange:
            query.update({'exchange' : exchange})

        if year:
            query.update({'year' : year})

        return self._requests.get(url=url, headers=headers, params=query)


    def dividend(self, ticker:str, date_from:str=None, date_to:str=None, year:str=None, exchange:str='nzx'):
        """
        Call financial/dividend endpoint to get stock dividend payout data
        :param ticker: ticker to search data for, eg air.nz
        :param date_from: in format YYYY-MM-DD
        :param date_to: in format YYYY-MM-DD
        :param exchange: exchange ticker is in
        :param year: year to search records for in format YYYY, eg 2020
        :return:
        """

        """
        Endpoint requires a valid token. Authorize client_id and client_secret first if token not passed
        """
        self.__authorize()

        url = url = f'{self._environment.value}/financial/dividend'
        headers = self.__generate_authorization_header()

        # check required parameters
        if not ticker:
            raise MissingTicker(
                "parameter `ticker` must be either passed"
            )

        # build query parameters for endpoint
        query = {'ticker' : ticker}

        if date_from:
            query.update({'date_from' : date_from})

        if date_to:
            query.update({'date_to' : date_to})

        if exchange:
            query.update({'exchange' : exchange})

        if year:
            query.update({'year' : year})

        return self._requests.get(url=url, headers=headers, params=query)


    def split(self, ticker:str, date_from:str=None, date_to:str=None, year:str=None, exchange:str='nzx'):
        """
        Call financial/split endpoint to get stock split ratio data
        :param ticker: ticker to search data for, eg air.nz
        :param date_from: in format YYYY-MM-DD
        :param date_to: in format YYYY-MM-DD
        :param exchange: exchange ticker is in
        :param year: year to search records for in format YYYY, eg 2020
        :return:
        """

        """
        Endpoint requires a valid token. Authorize client_id and client_secret first if token not passed
        """
        self.__authorize()

        url = url = f'{self._environment.value}/financial/split'
        headers = self.__generate_authorization_header()

        # check required parameters
        if not ticker:
            raise MissingTicker(
                "parameter `ticker` must be either passed"
            )

        # build query parameters for endpoint
        query = {'ticker' : ticker}

        if date_from:
            query.update({'date_from' : date_from})

        if date_to:
            query.update({'date_to' : date_to})

        if exchange:
            query.update({'exchange' : exchange})

        if year:
            query.update({'year' : year})

        return self._requests.get(url=url, headers=headers, params=query)

