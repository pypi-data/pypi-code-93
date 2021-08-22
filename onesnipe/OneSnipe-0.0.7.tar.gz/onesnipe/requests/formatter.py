#   Copyright 2021 Geographs
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
from json import dumps
from typing import Optional, Union
from urllib.parse import quote


def parse_content(content: Union[dict, str]) -> str:
    if isinstance(content, dict):
        return dumps(content)
    return quote(content)


class Formatter(object):
    def __init__(self, method: str,
                 host: str, path: str,
                 headers: Optional[dict], content: Union[dict, str, None] = None) -> None:
        """
        Initializes Formatter class

        :param method:
        :param host:
        :param path:
        :param headers:
        :param content:
        :return none:
        """
        self.method = method
        self.host = host
        self.path = path

        self.headers = headers
        self.content_type = "application/json" if isinstance(content, dict) else "application/x-www-form-urlencoded"
        self.content = parse_content(content) if content is not None else ""

    def format(self) -> bytes:
        """
        Formats into bytes to send through a socket

        :return data:
        """
        self.headers["Host"] = self.host

        if self.content != "":
            self.headers["Content-Type"] = self.content_type
            self.headers["Content-Length"] = len(self.content)

        headers = "\r\n".join(f"{x}: {y}" for x, y in self.headers.items())

        return bytes(f"{self.method} {self.path} HTTP/1.1\r\n{headers}\r\n\r\n{self.content}", "utf-8")
