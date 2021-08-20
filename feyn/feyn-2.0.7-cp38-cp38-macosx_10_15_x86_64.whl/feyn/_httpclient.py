"""
HttpClient based on requests, that takes care of setting up:
- The base url for the API
- Default headers
- And a retry policy

The returned client, has same interface as the requests module.
"""
import json
import logging
import re
from http import HTTPStatus
from typing import Iterable, Tuple

import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

WARNING_REGEX = re.compile(r"\s*(?P<component>[\S]+)\s+(?P<message>\"(?:[^\"\\]|\\.)*\")(?:,|$)")


class HttpClient(requests.Session):
    def __init__(self, api_base_url, default_headers=None):
        super().__init__()

        retry_policy = self._get_retry_policy()
        adapter = HTTPAdapter(max_retries=retry_policy)
        self.mount('http://', adapter)
        self.mount('https://', adapter)

        if default_headers:
            self.headers.update(default_headers)
        self.api_base_url = api_base_url

        if self.api_base_url.endswith("/"):
            raise ValueError("Dont end the api_base_url with a '/' please.")

    def request(self, method, url, *args, **kwargs):
        url = self._prepend_base_url(url)
        response = super().request(method, url, *args, **kwargs)

        # slightly abuse python's logging framework to show API warnings as if they were normal python warnings
        for component, message in iter_api_warnings(response.headers.get("Abzu-Warning", "")):
            logging.getLogger(component).warning(message)

        return response

    def _prepend_base_url(self, url):
        if not url.startswith("/"):
            raise ValueError("Start with a '/' please.")

        # Hack to be able to access the qlattice information on 'http:/.../api/v1/qlattice'.
        # Public facing api paths should be revisited to remove this hack.
        if url == "/":
            url = ""

        return self.api_base_url + url

    def _get_retry_policy(self) -> Retry:
        version = tuple(map(int, urllib3.__version__.split(".")))
        status_forcelist = [
            HTTPStatus.INTERNAL_SERVER_ERROR,
            HTTPStatus.BAD_GATEWAY,
            HTTPStatus.SERVICE_UNAVAILABLE,
            HTTPStatus.GATEWAY_TIMEOUT
        ]
        allowed_methods = ['GET', 'PUT', 'POST', 'DELETE']

        # the urllib3 interface changed in v1.26.0, but we still see people
        # using the older version even though we require `urllib3>=1.26.0`,
        # so try to support both for a while
        if version >= (1, 26, 0):
            return Retry(
                total=2,
                backoff_factor=2,
                raise_on_status=False,
                allowed_methods=allowed_methods,
                status_forcelist=status_forcelist,
            )
        else:
            return Retry(
                total=2,
                backoff_factor=2,
                raise_on_status=False,
                method_whitelist=allowed_methods,
                status_forcelist=status_forcelist,
            )


def iter_api_warnings(header_string) -> Iterable[Tuple[str, str]]:
    # yield all warnings matching the following format:
    # component "json quoted string"{, component "json quoted string"}*
    for match in WARNING_REGEX.finditer(header_string):
        yield match["component"], json.loads(match["message"])
