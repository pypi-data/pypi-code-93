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
from random import choice
from string import ascii_letters, digits
from time import time

from onesnipe.console import console
from onesnipe.requests import Request


class Offset(object):
    def __init__(self, requests: int) -> None:
        """
        Initializes Offset class

        :param requests:
        :return none:
        """
        self.charset = ascii_letters + digits
        self.requests = [self.create_request() for _ in range(requests)]
        self.amount = requests

    def create_request(self) -> Request:
        """
        Creates request

        :return request:
        """
        return Request(
            method="PUT",
            url=f"https://api.minecraftservices.com/minecraft/profile/name/"
                f"{''.join([choice(self.charset) for _ in range(5)])}",
            headers={
                "Authorization": f"Bearer {''.join([choice(self.charset) for _ in range(300)])}"
            }
        )

    async def find(self) -> None:
        """
        Finds offset

        :return none:
        """
        console.info("Finding offset...")

        try:
            await asyncio.gather(*[request.connect() for request in self.requests])
        except Exception as exc:
            console.error(exc)
            return

        drop = int(time()) + 3

        await asyncio.sleep(drop - time())

        try:
            responses = await asyncio.gather(*[request.send() for request in self.requests])
        except Exception as exc:
            console.error(exc)
            return

        offset = int((sum([resp[1] - drop for resp in responses]) / self.amount) * 1000)
        console.info(f"Your offset is {offset} ms.")
