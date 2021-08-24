import json
from collections.abc import Mapping
from typing import Optional


class BaseAdapter:
    def request_headers(self) -> Mapping[str, str]:
        raise NotImplementedError  # pragma: no cover

    def request_params(self) -> Mapping[str, str]:
        raise NotImplementedError  # pragma: no cover

    def redirect_uri(self, response) -> Optional[str]:
        raise NotImplementedError  # pragma: no cover

    def set_redirect_uri(self, response, uri):
        raise NotImplementedError  # pragma: no cover

    def set_headers(self, response, headers):
        raise NotImplementedError  # pragma: no cover

    def set_cookie(self, response, needs_cookie=False):
        raise NotImplementedError  # pragma: no cover

    @property
    def method(self):
        raise NotImplementedError  # pragma: no cover

    @property
    def location(self):
        raise NotImplementedError  # pragma: no cover

    def deserialize_data(self, data: str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return None

    def serialize_data(self, data) -> str:
        return json.dumps(data, separators=(",", ":"))


class SimpleAdapter(BaseAdapter):
    def __init__(
        self,
        method="GET",
        location="/",
        headers=None,
        params=None,
        redirect_uri=None,
    ):
        self._method = method
        self._location = location
        self.headers = headers or {}
        self.params = params or {}
        self._redirect_uri = redirect_uri
        self.response_redirect_uri = None
        self.response_headers = None
        self.cookie = None

    def request_headers(self) -> Mapping[str, str]:
        return self.headers

    def request_params(self) -> Mapping[str, str]:
        return self.params

    def redirect_uri(self, response) -> Optional[str]:
        return self._redirect_uri

    def set_redirect_uri(self, response, uri):
        self.response_redirect_uri = uri

    def set_headers(self, response, headers):
        self.response_headers = headers

    def set_cookie(self, response, needs_cookie):
        self.cookie = needs_cookie

    @property
    def method(self):
        return self._method

    @property
    def location(self):
        return self._location
