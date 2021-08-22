"""Endpoint definitions
"""
import logging
from abc import ABC
from abc import abstractmethod

from typing import Union


import urllib3  # type: ignore
import requests

# pylint: disable=import-error
from url_normalize import url_normalize  # type: ignore

from .typing import JSON
# pylint: disable=too-few-public-methods
# pylint: disable=missing-docstring


# string representation of JSON data
# this type is local to this module, since it's used only in private classes like the RESTHTTPClient
JSON_STR = str  # pylint: disable=invalid-name

LOGGER = logging.getLogger("requests.packages.urllib3")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class HTTPRequestNotOK(Exception):
    def __init__(self, content, status_code: int):
        self.status_code = status_code
        self.content = content

        super().__init__(f"{status_code}: {content}")


def enable_http_transactions_debug():
    # pylint: disable=import-outside-toplevel
    import http.client as http_client
    # pylint: enable=import-outside-toplevel

    http_client.HTTPConnection.debuglevel = 1
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


class RESTHTTPClient:
    def __init__(self, endpoint_url: str, headers: dict = None):
        self._endpoint_url = endpoint_url
        self._headers = {}

        if headers is not None:
            self._headers.update(headers)


    def post(self, path: str, data: Union[JSON_STR,JSON]) -> JSON:
        """Send a POST request to path

        Send a POST request to the endpoint using path and data.

        Arguments:
            - data (JSON_STR,JSON): either a string representing JSON, or python objects which can be serialised
              into JSON

        Raises:
            HTTPRequestNotOK: when the HTTP operation does not return OK

        Returns:
            JSON: a python data structures representing the JSON response
        """
        url = url_normalize('%s/%s' % (self._endpoint_url, path))
        headers = self._headers.copy()
        headers['Content-Type'] = "application/json"

        response = requests.request('POST',
                url=url_normalize(url),
                headers=headers,
                data=data,
                verify=False)


        json_response = response.json()

        if not response.ok:
            raise HTTPRequestNotOK(json_response, response.status_code)

        LOGGER.debug('request: POST: %s', url)
        LOGGER.debug('request: POST: %s', data)
        LOGGER.debug('response: %s', json_response)

        return json_response

    def put(self, path: str, data: Union[JSON_STR,JSON]) -> JSON:
        """Send a PUT request to path

        Send a PUT request to the endpoint using path and data.

        Arguments:
            - data (JSON_STR,JSON): either a string representing JSON, or python objects which can be serialised
              into JSON

        Raises:
            HTTPRequestNotOK: when the HTTP operation does not return OK

        Returns:
            JSON: a python data structures representing the JSON response
        """
        url = url_normalize('%s/%s' % (self._endpoint_url, path))
        headers = self._headers.copy()
        headers['Content-Type'] = "application/json"

        response = requests.request('PUT',
                url=url_normalize(url),
                headers=headers,
                data=data,
                verify=False)

        json_response = response.json()

        if not response.ok:
            raise HTTPRequestNotOK(json_response, response.status_code)

        LOGGER.debug('request: PUT: %s', url)
        LOGGER.debug('request: PUT: %s', data)
        LOGGER.debug('response: %s', json_response)

        return json_response



    def get(self, path: str) -> JSON:
        """Send a GET request to path

        Send a GET request to the endpoint using path

        Raises:
            HTTPRequestNotOK: when the HTTP operation does not return OK

        Returns:
            JSON: a python data structures representing the JSON response
        """
        url = url_normalize('%s/%s' % (self._endpoint_url, path))
        response = requests.request('GET',
                url=url,
                headers = self._headers,
                verify=False)

        json_response = response.json()

        if not response.ok:
            raise HTTPRequestNotOK(json_response, response.status_code)

        LOGGER.debug('request: GET: %s', url)
        LOGGER.debug('response: %s', json_response)

        return json_response


class IEndpoint(ABC):
    @abstractmethod
    def read(self, path: str) -> JSON:
        ...

    @abstractmethod
    def create(self, path: str, data: str) -> JSON:
        ...

    @abstractmethod
    def update(self, path: str, data: str) -> JSON:
        ...


class GitLabEndpoint(IEndpoint):
    def __init__(self, endpoint_url: str, token: str = None):
        headers = {}

        if token is not None:
            headers["PRIVATE-TOKEN"] = token

        self._rest_client = RESTHTTPClient(endpoint_url, headers=headers)

    def read(self, path: str) -> JSON:
        # get returns a JSON type, but here the code is dealing only with returns that we are sure they are dict
        return self._rest_client.get(path)

    def create(self, path: str, data: JSON) -> JSON:
        return self._rest_client.post(path, data)

    def update(self, path: str, data: JSON) -> JSON:
        return self._rest_client.put(path, data)


class GitLabDotCom(GitLabEndpoint):
    """Gitlab.com endpoint"""
    def __init__(self, token=None) -> None:
        super().__init__("https://gitlab.com/api/v4", token)
