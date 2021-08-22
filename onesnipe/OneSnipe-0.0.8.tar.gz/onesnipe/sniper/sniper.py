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

from aiohttp import ClientSession, client_exceptions

from onesnipe.console import console
from onesnipe.constants import DROPAPI
from onesnipe.requests import Request


class Sniper(object):
    def __init__(self, bearer: str, username: str, offset: float, account_type: str = "mojang") -> None:
        """
        Initializes Sniper class

        :param bearer:
        :param username:
        :param offset:
        :return none:
        :raises ValueError:
        """
        self.bearer = bearer
        self.username = username
        self.offset = offset
        self.account_type = account_type.lower()

        if self.account_type not in ("mojang", "microsoft", "giftcard"):
            raise ValueError("account_type must be either mojang, microsoft, or giftcard")

    async def get_droptime(self) -> float:
        """
        Attempts to get a username's drop time in unix
        If fails asks for manual input

        :return unix:
        """
        for api in DROPAPI:
            try:
                async with ClientSession() as session:
                    response = await session.get(
                        url=DROPAPI[api]["endpoint"].format(self.username),
                        headers=DROPAPI[api]["headers"]
                    )

                    return float((await response.json())[DROPAPI[api]["key"]])
            except (OSError, IOError, KeyError, ValueError, client_exceptions.ClientResponseError):
                pass

        while True:
            console.info("Failed to find the drop time. Please manually input it.")

            try:
                return float(input("Drop Time: "))
            except ValueError:
                pass

    async def create_request(self) -> Request:
        """
        Creates request

        :return request:
        """
        if self.account_type == "mojang":
            return Request(
                method="PUT",
                url=f"https://api.minecraftservices.com/minecraft/profile/name/{self.username}",
                headers={
                    "Authorization": f"Bearer {self.bearer}"
                }
            )
        else:
            return Request(
                method="POST",
                url="https://api.minecraftservices.com/minecraft/profile",
                headers={
                    "Authorization": f"Bearer {self.bearer}"
                },
                content={
                    "profileName": self.username
                }
            )

    async def snipe(self) -> None:
        """
        Snipes a username

        :return none:
        """
        droptime = await self.get_droptime()
        request_time = droptime - self.offset

        requests = await asyncio.gather(*[self.create_request() for _ in range(6 if self.account_type == "giftcard" else 3)])

        if droptime < time():
            console.error("This username has already dropped.")
            return

        console.info(f"`{self.username}` dropping in {droptime - int(time())} seconds...")

        await asyncio.sleep(request_time - time() - 5)

        console.info("Connecting to API...")

        try:
            await asyncio.gather(*[request.connect() for request in requests])
        except Exception as exc:
            console.error(exc)
            return

        await asyncio.sleep(request_time - time())

        try:
            responses = await asyncio.gather(*[request.send() for request in requests])
        except Exception as exc:
            console.error(exc)
            return

        for response in responses:
            console.info(f"Received {response[0]} @ {response[1]}")
