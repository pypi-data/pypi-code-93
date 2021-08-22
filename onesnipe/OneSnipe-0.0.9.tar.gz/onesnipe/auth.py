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
from re import findall

from aiohttp import ClientSession
from msmcauth import login


class Auth(object):
    @staticmethod
    def microsoft(email: str, password: str) -> str:
        """
        Logs into a Microsoft account and gets the bearer token

        :param email:
        :param password:
        :return bearer:
        """
        return login(email, password).access_token

    @staticmethod
    async def mojang(email: str, password: str) -> str:
        """
        Logs into a Mojang account and gets the bearer token

        :param email:
        :param password:
        :returns bearer:
        """
        async with ClientSession() as session:
            pre_resp = await session.get(
                url="https://account.mojang.com/login",
                headers={
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,"
                              "image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "accept-encoding": "gzip, deflate, br",
                    "accept-language": "en-US,en;q=0.9",
                    "sec-fetch-dest": "document",
                    "sec-fetch-mode": "navigate",
                    "sec-fetch-site": "none",
                    "upgrade-insecure-requests": "1",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                  "Chrome/92.0.4515.159 Safari/537.36"
                }
            )

            play_session = dict(pre_resp.cookies)["PLAY_SESSION"]
            authenticity_token = findall("name=\"authenticityToken\" value=\"(.*?)\"", await pre_resp.text("utf-8"))

            response = await session.post(
                url="https://account.mojang.com/login",
                headers={
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,"
                              "image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "accept-encoding": "gzip, deflate, br",
                    "accept-language": "en-US,en;q=0.9",
                    "cache-control": "max-age=0",
                    "content-type": "application/x-www-form-urlencoded",
                    "cookie": f"PLAY_SESSION={play_session}; MSCC=NR",
                    "origin": "https://account.mojang.com",
                    "referer": "https://account.mojang.com/login",
                    "sec-fetch-dest": "document",
                    "sec-fetch-mode": "navigate",
                    "sec-fetch-site": "same-origin",
                    "upgrade-insecure-requests": "1",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                  "Chrome/92.0.4515.159 Safari/537.36"
                },
                data=f"authenticityToken={authenticity_token}&username={email}&password={password}"
            )

            return findall("accessToken=(.*?)&___ID=", str(response.cookies))[0]
