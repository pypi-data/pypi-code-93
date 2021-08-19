import logging
import re
from json import JSONEncoder, JSONDecoder
from typing import Dict, Any, cast, Optional

import requests
from requests import Response

DEFAULT_API_ENDPOINT = "http://localhost:4000"

logger = logging.getLogger("vectice.http")


class HttpError(Exception):
    def __init__(self, code: int, reason: str, path: str, method: str, json: Optional[str]):
        super().__init__()
        self.code: int = code
        self.reason: str = reason
        self.path = path
        self.method = method
        self.json = json

    def __str__(self):
        return f"""HTTP Error Code {self.code} : {self.reason}
        {self.method} {self.path}

        {self.json}
        """


def format_url(url: str) -> str:
    """Add https protocol if missing and remove trailing slash."""
    url = url.rstrip("/")
    if not re.match("(?:http|https|ftp)://", url):
        return "https://{}".format(url)
    return url


class VecticeEncoder(JSONEncoder):
    """
    Json Encoder with 2 specific behaviors:
    - handle datetime types so be serialized as a string following ISO8601 format
    - remove any null property from the serialized json.
    """

    def default(self, obj: Any) -> Any:
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        internal_copy = obj.__dict__.copy()
        return {k: v for (k, v) in internal_copy.items() if v is not None}


# DecodedType = TypeVar('DecodedType')


class Connection:
    def __init__(self, api_endpoint: Optional[str] = None):
        self._API_BASE_URL = format_url(api_endpoint or DEFAULT_API_ENDPOINT)
        self._request_headers: Dict[str, str] = {}

    @property
    def api_base_url(self) -> str:
        return self._API_BASE_URL

    def _get(self, path: str) -> Dict[str, Any]:
        self._request_headers["Content-Type"] = "application/json"
        response = requests.get(url=self.api_base_url + path, headers=self._request_headers)
        return self._response(self.api_base_url + path, response, "GET")

    def _post(self, path: str, payload: Dict[str, Any] = None, decoder=JSONDecoder) -> Dict[str, Any]:
        self._request_headers["Content-Type"] = "application/json"
        data = VecticeEncoder(indent=1).encode(payload)
        response = requests.post(url=self.api_base_url + path, headers=self._request_headers, data=data)
        return self._response(self.api_base_url + path, response, "POST", payload)

    def _put(self, path: str, payload: Any = None, decoder=JSONDecoder, cls=dict) -> Dict[str, Any]:
        self._request_headers["Content-Type"] = "application/json"
        data = VecticeEncoder().encode(payload)
        response = requests.put(url=self.api_base_url + path, headers=self._request_headers, data=data)
        return self._response(self.api_base_url + path, response, "PUT", payload)

    def _response(
        self, path: str, response: Response, method: str, payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        self.raise_status(path, response, method, payload)
        logger.debug(f"{method} {path} {response.status_code}")
        logger.debug("\n".join(f"{item[0]}: {item[1]}" for item in self._request_headers.items()))
        logger.debug(VecticeEncoder(indent=4, sort_keys=True).encode(payload))
        return cast(Dict[str, Any], response.json())

    @classmethod
    def raise_status(cls, path: str, response: Response, method: str, payload: Optional[Dict[str, Any]]) -> None:
        if not (200 <= response.status_code < 300):
            reason = response.text
            json = VecticeEncoder(indent=4, sort_keys=True).encode(payload) if payload is not None else None
            raise HttpError(response.status_code, reason, path, method, json)
