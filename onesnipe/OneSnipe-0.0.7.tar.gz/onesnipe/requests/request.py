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
import asyncio
from time import time
from typing import Optional, Union
from urllib.parse import urlparse

from onesnipe.console import console
from onesnipe.requests.formatter import Formatter


class Request(object):
    def __init__(self, method: str,
                 url: str, headers: Optional[dict],
                 content: Union[dict, str, None] = None) -> None:
        """
        Initializes Request class

        :param method:
        :param url:
        :param headers:
        :param content:
        :return none:
        """
        parse = urlparse(url)

        self.host = parse.hostname
        self.port = 443 if parse.scheme == "https" else 80

        self.headers = headers
        self.payload = Formatter(
            method=method,
            host=self.host,
            path=parse.path,
            headers=headers,
            content=content
        ).format()

        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None

    async def connect(self) -> None:
        """
        Connects to host

        :return:
        """
        self.reader, self.writer = await asyncio.open_connection(
            host=self.host,
            port=self.port,
            ssl=True if self.port == 443 else False
        )

    async def send(self) -> tuple[str, float]:
        """
        Sends data

        :return status, time:
        """
        console.error(self.payload)
        self.writer.write(self.payload)
        await self.writer.drain()
        return await self.get_status_code(), time()

    async def get_status_code(self) -> str:
        """
        Gets status code

        :return status:
        """
        return str(await self.reader.read(12), "utf-8")[9:12]
