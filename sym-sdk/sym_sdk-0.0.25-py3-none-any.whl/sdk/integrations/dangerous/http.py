"""The HTTP Integration allows arbitrary HTTP requests to be made to remote servers.

The API is similar to that of the :mod:`~requests` library.
"""

from typing import Dict, Literal, Optional, Union

from requests import Request, Response, Session

HTTPMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]


class SymRequest(object):
    """Wraps a URL that you might make a request to.

    Handles sharing a :class:`~requests.Session` across a host.
    """

    def __init__(self, url: str, session: Optional[Session] = None):
        self.url = url

        if session:
            self.session = session
            self.close_session = False
        else:
            self.session = Session()
            self.close_session = True

    def __del__(self):
        if self.close_session:
            self.session.close()

    def __truediv__(self, path: str):
        return self.with_path(path)

    def with_path(self, path: str):
        """Returns a :class:`~requests.SymRequest` with the specified sub-path

        You can also use the / operator as a shortcut for this method.
        """

        return self.__class__(f"{self.url}/{path}", session=self.session)

    def go(
        self,
        method: HTTPMethod,
        data: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Response:
        """Executes a request and caches the response."""

        self.req = Request(method, self.url, data=data, headers=headers or {}).prepare()
        self.resp = self.session.send(self.req)
        return self.resp

    def parsed(self):
        try:
            return self.resp.json()
        except ValueError:
            return self.resp.text


def request(url: str, method: HTTPMethod, body: Optional[Dict] = None):
    """Makes an HTTP request to the given URL with the specified method and body.

    If the response is valid JSON, a dictionary is returned, otherwise, a string is returned.
    """

    req = SymRequest(url)
    req.go(method, data=body or {})
    return req.parsed()


def get(url: str) -> Union[str, dict]:
    """Makes a GET request to the given URL.

    If the response is valid JSON, a dictionary is returned, otherwise, a string is returned.
    """

    return request(url, "GET")


def post(url: str, body: Optional[Dict] = None) -> Union[str, dict]:
    """Makes a POST request to the given URL, with the specified body.

    If the response is valid JSON, a dictionary is returned, otherwise, a string is returned.
    """

    return request(url, "POST", body or {})


def put(url: str, body: Optional[Dict] = None) -> Union[str, dict]:
    """Makes a PUT request to the given URL, with the specified body.

    If the response is valid JSON, a dictionary is returned, otherwise, a string is returned.
    """

    return request(url, "PUT", body or {})


def patch(url: str, body: Optional[Dict] = None) -> Union[str, dict]:
    """Makes a PATCH request to the given URL, with the specified body.

    If the response is valid JSON, a dictionary is returned, otherwise, a string is returned.
    """

    return request(url, "PATCH", body or {})


def delete(url: str, body: Optional[Dict] = None) -> Union[str, dict]:
    """Makes a DELETE request to the given URL, with the specified body.

    If the response is valid JSON, a dictionary is returned, otherwise, a string is returned.
    """

    return request(url, "DELETE", body or {})
