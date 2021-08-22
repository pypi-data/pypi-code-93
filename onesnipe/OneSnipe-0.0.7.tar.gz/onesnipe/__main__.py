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
from typing import Optional

from typer import Typer

from onesnipe.auth import Auth
from onesnipe.console import console
from onesnipe.constants import ASCII
from onesnipe.functions import clear
from onesnipe.sniper import Sniper, Offset

app = Typer(add_completion=False)


@app.command("snipe", short_help="Snipes a Username")
def _snipe(username: str, offset: float,
           bearer: Optional[str] = None, email: Optional[str] = None,
           password: Optional[str] = None, account_type: str = "mojang") -> None:
    """
    Snipes a username

    :param username:
    :param offset:
    :param bearer:
    :param email:
    :param password:
    :param account_type:
    :return none:
    """
    account_type = account_type.lower()

    if bearer is None and email is None and password is None:
        console.error("Must have an auth method.")
        return
    elif bearer is None and email is None:
        console.error("Missing password argument.")
        return
    elif bearer is None and password is None:
        console.error("Missing email argument.")
        return
    elif account_type not in ("mojang", "microsoft", "giftcard"):
        console.error("type must be either mojang, microsoft, or giftcard")
        return

    loop = asyncio.get_event_loop()

    try:
        if email is not None and password is not None:
            if type == "mojang":
                bearer = loop.run_until_complete(Auth.mojang(email, password))
            bearer = Auth.microsoft(email, password)
    except Exception as exc:
        console.error(exc)
        return

    loop.run_until_complete(Sniper(
        bearer=bearer,
        username=username,
        offset=offset / 1000,
        account_type=account_type
    ).snipe())


@app.command("offset", short_help="Finds Your Offset")
def _offset(requests: int = 3) -> None:
    """
    Finds offset

    :param requests:
    :return none:
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Offset(
        requests=requests
    ).find())


def main() -> None:
    """
    Main function

    :return none:
    """
    asyncio.set_event_loop(asyncio.ProactorEventLoop())
    clear()
    print(ASCII)
    console.info("Welcome to OneSnipe - Created by Geographs#0404\n")
    app()


if __name__ == "__main__":
    main()
