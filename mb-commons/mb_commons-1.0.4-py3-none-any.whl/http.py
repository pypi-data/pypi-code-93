import json
from dataclasses import dataclass, field
from json import JSONDecodeError
from typing import Any, Optional

import requests

FIREFOX_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:82.0) Gecko/20100101 Firefox/82.0"
CHROME_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"  # noqa


@dataclass
class HResponse:
    """HTTP Response"""

    http_code: int = 0
    error: Optional[str] = None
    body: str = ""
    headers: dict = field(default_factory=lambda: {})

    _json_data: dict = field(default_factory=lambda: {})
    _json_parsed = False
    _json_parsed_error = False

    @property
    def json(self) -> Any:
        if not self._json_parsed:
            self._parse_json()
        return self._json_data

    @property
    def json_parse_error(self) -> bool:
        if not self._json_parsed:
            self._parse_json()
        return self._json_parsed_error

    def to_error(self, error=None):
        from mb_commons import Result

        return Result(error=error if error else self.error, data=self)

    def to_ok(self, result: Any):
        from mb_commons import Result

        return Result(ok=result, data=self)

    def is_error(self):
        return self.error is not None

    def is_timeout_error(self):
        return self.error == "timeout"

    def is_proxy_error(self):
        return self.error == "proxy_error"

    def is_connection_error(self):
        return self.error and self.error.startswith("connection_error:")

    def _parse_json(self):
        try:
            self._json_data = {}
            self._json_data = json.loads(self.body)
            self._json_parsed_error = False
        except JSONDecodeError:
            self._json_parsed_error = True
        self._json_parsed = True


def hrequest(
    url: str,
    *,
    method="GET",
    proxy: Optional[str] = None,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
    cookies: Optional[dict] = None,
    timeout=10,
    user_agent: Optional[str] = None,
    json_params=False,
    auth=None,
) -> HResponse:
    method = method.upper()
    proxies = {"http": proxy, "https": proxy} if proxy else None
    if not headers:
        headers = {}
    try:
        headers["user-agent"] = user_agent
        if method == "GET":
            r = requests.get(
                url,
                proxies=proxies,
                timeout=timeout,
                headers=headers,
                cookies=cookies,
                params=params,
                auth=auth,
            )
        elif method == "POST":
            if json_params:
                r = requests.post(
                    url,
                    proxies=proxies,
                    timeout=timeout,
                    headers=headers,
                    cookies=cookies,
                    json=params,
                    auth=auth,
                )
            else:
                r = requests.post(
                    url,
                    proxies=proxies,
                    timeout=timeout,
                    headers=headers,
                    cookies=cookies,
                    data=params,
                    auth=auth,
                )
        elif method == "PUT":
            if json_params:
                r = requests.put(
                    url,
                    proxies=proxies,
                    timeout=timeout,
                    headers=headers,
                    cookies=cookies,
                    json=params,
                    auth=auth,
                )
            else:
                r = requests.put(
                    url,
                    proxies=proxies,
                    timeout=timeout,
                    headers=headers,
                    cookies=cookies,
                    data=params,
                    auth=auth,
                )
        elif method == "DELETE":
            if json_params:
                r = requests.delete(
                    url,
                    proxies=proxies,
                    timeout=timeout,
                    headers=headers,
                    cookies=cookies,
                    json=params,
                    auth=auth,
                )
            else:
                r = requests.delete(
                    url,
                    proxies=proxies,
                    timeout=timeout,
                    headers=headers,
                    cookies=cookies,
                    data=params,
                    auth=auth,
                )
        else:
            raise ValueError(method)
        return HResponse(http_code=r.status_code, body=r.text, headers=dict(r.headers))
    except requests.exceptions.Timeout:
        return HResponse(error="timeout")
    except requests.exceptions.ProxyError:
        return HResponse(error="proxy_error")
    except requests.exceptions.ConnectionError as e:
        return HResponse(error=f"connection_error: {str(e)}")
    except Exception as err:
        return HResponse(error=f"exception: {str(err)}")
