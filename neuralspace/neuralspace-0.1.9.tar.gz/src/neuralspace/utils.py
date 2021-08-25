import json
import logging
import os
from copy import copy
from pathlib import Path
from typing import Any, Dict, List, Text

from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from neuralspace.apis import get_async_http_session
from neuralspace.constants import (
    APP_IS_INSTALLED,
    AUTHORIZATION,
    COMMON_HEADERS,
    END_INDEX,
    FROM,
    INSTALL_APP_COMMAND,
    INSTALL_APP_URL,
    LOGIN_URL,
    START_INDEX,
    TIME,
    TO,
    TYPE,
    VALUE,
    auth_path,
    neuralspace_url,
)

logger = logging.getLogger("rich")
console = Console()


def setup_logger(log_level: Text):
    logging.basicConfig(level=log_level, handlers=[RichHandler()])


def get_logo():
    logo_path = (Path(os.path.realpath(__file__))).parent / "data" / "logo.txt"
    return f"{logo_path.read_text()}"


def print_logo():
    logo_path = (Path(os.path.realpath(__file__))).parent / "data" / "logo.txt"
    console.print(f"\n[bold]{logo_path.read_text()}[/bold]", style="#c47900")


def register_auth_token(login_response: Dict[Text, Text]):
    if "data" in login_response and "auth" in login_response["data"]:
        with open(str(auth_path()), "w") as f:
            json.dump(login_response, f)
    else:
        raise ValueError(f"Login response is malformed: {login_response}")


def get_auth_token() -> Text:
    if auth_path().exists():
        credentials = json.loads(auth_path().read_text())
        return credentials["data"]["auth"]
    else:
        raise FileNotFoundError(
            "Credentials file not found. Consider logging in using."
            " Seems like you have not logged in. "
            "`neuralspace login --email <your-neuralspace-email-id> "
            "--password <your-password>`"
        )


def is_success_status(status_code: int) -> bool:
    success = False
    if 200 <= status_code < 300:
        success = True
    return success


async def do_login(email: Text, password: Text):
    user_data = {"email": email, "password": password}
    logger.debug(f"Login🚪 attempt for: {user_data}")
    async with get_async_http_session().post(
        url=f"{neuralspace_url()}/{LOGIN_URL}",
        data=json.dumps(user_data),
        headers=COMMON_HEADERS,
    ) as response:
        json_response = await response.json(encoding="utf-8")
        if is_success_status(response.status):
            register_auth_token(json_response)
            console.print(
                "> [deep_sky_blue2]INFO[/deep_sky_blue2] ✅  Login successful!"
            )
            console.print(
                f"> [deep_sky_blue2]INFO[/deep_sky_blue2] 🗝 Credentials registered at {auth_path()}"
            )
            console.print(
                f"⏩  Install an app: [dark_orange3]{INSTALL_APP_COMMAND}[/dark_orange3]"
            )
        else:
            console.print("Login failed ❌! Please check your username and password")


async def app_install(name: Text):
    user_data = {"appType": name}
    logger.debug(f"Installing app: {name}")
    HEADERS = copy(COMMON_HEADERS)
    HEADERS[AUTHORIZATION] = get_auth_token()
    async with get_async_http_session().post(
        url=f"{neuralspace_url()}/{INSTALL_APP_URL}",
        data=json.dumps(user_data),
        headers=HEADERS,
    ) as response:
        json_response = await response.json(encoding="utf-8")
        if is_success_status(response.status):
            register_auth_token(json_response)
            console.print(
                "> [deep_sky_blue2]INFO[/deep_sky_blue2] ✅ Install Successful!"
            )
        else:
            if json_response["message"] == APP_IS_INSTALLED:
                console.print(
                    f"> [deep_sky_blue2]INFO[/deep_sky_blue2] [dark_orange3]{APP_IS_INSTALLED}dark_orange3"
                )
                console.print("")
            else:
                console.print(" ❌ Install Failed!")
                console.print(
                    f"\n{json.dumps(json_response, indent=4, ensure_ascii=False)}"
                )


def get_list_chunks(items: List[Any], chunk_size: int):
    for chunk in range(0, len(items), chunk_size):
        yield items[chunk : chunk + chunk_size]  # noqa : E203


def add_apps_to_table(table: Table) -> Table:
    table.add_row(
        "[bold]nlu[/bold]",
        "neuralspace [bold red]nlu[/bold red]",
        "Whether you are using chatbots, voicebots, or process automation engines, they are all powered by Natural "
        "Language Understanding (NLU). It's main purpose is to "
        "understand the intent of the user, and extract relevant "
        "information (entities) from what they said (speech) or wrote (text) to perform a relevant action. "
        "Entities can be anything from names, addresses, account numbers to very domain specific terms like names of "
        "chemicals, medicines, etc. Sometimes it also predicts the sentiment of the user which helps the bot respond "
        "to the user in a more empathetic tone.",
    )
    table.add_row(
        "[bold]ner[/bold]",
        "neuralspace [bold red]ner[/bold red]",
        "Entities play a major role in language understanding. To perform an action on a certain user query you not "
        "only need to understand the intent behind it but also the entities present in it. "
        "E.g., if someone says 'flights from Berlin to London', the intent here is flight-search and entities are "
        "Berlin and London, which are of type city. In a given piece of text, entities can be anything from names, "
        "addresses, account numbers to very domain specific terms like names of chemicals, medicines, etc. "
        "Essentially any valuable information that can be extracted from text.",
    )
    return table


def add_heading_to_description_table(table: Table) -> Table:
    table.add_column("Name", style="#c47900")
    table.add_column("Command", style="#c47900")
    table.add_column("Description")
    return table


def print_logo_and_description():
    console.print(f"[bold]{get_logo()}[/bold]", style="#c47900")
    console.print(
        "[bold magenta]Website: [/bold magenta][link]https://neuralspace.ai[/link]"
    )
    console.print(
        "[bold magenta]Docs: [/bold magenta][link]https://docs.neuralspace.ai[/link]"
    )
    console.print(
        "[bold magenta]Platform Login: [/bold magenta][link]https://platform.neuralspace.ai[/link]"
    )
    console.print("[bold magenta]Commands: [/bold magenta]")
    table = Table(show_header=True, header_style="bold #c47900", show_lines=True)
    table = add_heading_to_description_table(table)
    table.add_row(
        "[bold]Login[/bold]",
        "neuralspace [bold red]login[/bold red]",
        "Login to the our platform and save credentials locally",
    )
    table.add_row(
        "[bold]List Apps[/bold]",
        "neuralspace [bold red]list-apps[/bold red]",
        "List all the available apps in our platform and their respective codes",
    )
    table.add_row(
        "[bold]Install App[/bold]",
        "neuralspace [bold red]install-app[/bold red]",
        "Installs the specific app on your account",
    )
    table = add_apps_to_table(table)
    console.print(table)


def print_ner_response(response: Dict[Text, Text], original_text: Text):
    list_of_entities = response["data"]["entities"]
    if not list_of_entities:
        console.print(
            f"There is no entities in your text: [bold red]{original_text}[/bold red]"
        )
    else:
        table = Table(show_header=True, header_style="orange3")
        table.add_column("idx", style="sandy_brown")
        table.add_column("Type", style="green")
        table.add_column("Value", style="green")
        table.add_column("Entities marked in original text")
        for i, entities in enumerate(list_of_entities):
            start_index = entities[START_INDEX]
            end_index = entities[END_INDEX]
            marked_sentence = ""
            for idx, character in enumerate(original_text):
                if start_index == 0:
                    marked_sentence += "[bold green]"
                if idx == start_index:
                    marked_sentence += "[bold green]"
                elif idx == end_index:
                    marked_sentence += "[/bold green]"
                marked_sentence += character
            if entities[TYPE] == TIME and isinstance(entities[VALUE], dict):
                type_time_format = (
                    f"From: {str(entities[VALUE][FROM])} To: {str(entities[VALUE][TO])}"
                )
                table.add_row(str(i), entities[TYPE], type_time_format, marked_sentence)
            else:
                table.add_row(str(i), entities[TYPE], entities[VALUE], marked_sentence)
        console.print(table)
