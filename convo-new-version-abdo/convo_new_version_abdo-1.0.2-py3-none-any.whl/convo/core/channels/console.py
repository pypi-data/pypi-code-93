# this builtin is needed so we can overwrite in test
import asyncio
import json
import logging
import os

import aiohttp
import questionary
from aiohttp import ClientTimeout
from prompt_toolkit.styles import Style
from typing import Any
from typing import Text, Optional, Dict, List

import convo.shared.utils.cli
import convo.shared.utils.io
from convo.cli import utils as cli_utils
from convo.core import utils
from convo.core.channels.rest import RestApiInput
from convo.core.constants import BY_DEFAULT_SERVER_URL
from convo.shared.constants import INTENT_MSG_PREFIX 
from convo.shared.utils.io import ENCODING_DEFAULT

logs = logging.getLogger(__name__)

STREAM_READING_TIMEOUT_ENVIRONMENT = "CONVO_SHELL_STREAM_READING_TIMEOUT_IN_SECONDS"
DEFAULT_STREAM_READ_TIMEOUT_IN_SECS = 10


def print_button(
    message: Dict[Text, Any],
    is_latest_message: bool = False,
    color=convo.shared.utils.io.bcolours.OK_BLUE,
) -> Optional[questionary.Question]:
    if is_latest_message:
        options = cli_utils.button_choices_from_msg_data_set(
            message, allow_free_text_input=True
        )
        ques = questionary.select(
            message.get("text"),
            options,
            style=Style([("qmark", "#6d91d3"), ("", "#6d91d3"), ("answer", "#b373d6")]),
        )
        return ques
    else:
        convo.shared.utils.cli.printing_color("Buttons:", color=color)
        for idx, button in enumerate(message.get("buttons")):
            convo.shared.utils.cli.printing_color(
                cli_utils.button_to_str(button, idx), color=color
            )


def print_bot_result(
    message: Dict[Text, Any],
    is_latest_message: bool = False,
    color=convo.shared.utils.io.bcolours.OK_BLUE,
) -> Optional[questionary.Question]:
    if "buttons" in message:
        ques = print_button(message, is_latest_message, color)
        if ques:
            return ques

    if "text" in message:
        convo.shared.utils.cli.printing_color(message.get("text"), color=color)

    if "image" in message:
        convo.shared.utils.cli.printing_color("Image: " + message.get("image"), color=color)

    if "attachment" in message:
        convo.shared.utils.cli.printing_color(
            "Attachment: " + message.get("attachment"), color=color
        )

    if "elements" in message:
        convo.shared.utils.cli.printing_color("Elements:", color=color)
        for idx, element in enumerate(message.get("elements")):
            convo.shared.utils.cli.printing_color(
                cli_utils.element_to_str(element, idx), color=color
            )

    if "quick_replies" in message:
        convo.shared.utils.cli.printing_color("Quick Replies:", color=color)
        for idx, element in enumerate(message.get("quick_replies")):
            convo.shared.utils.cli.printing_color(
                cli_utils.button_to_str(element, idx), color=color
            )

    if "custom" in message:
        convo.shared.utils.cli.printing_color("Custom json:", color=color)
        convo.shared.utils.cli.printing_color(
            json.dumps(message.get("custom"), indent=2), color=color
        )


def fetch_user_input(previous_response: Optional[Dict[str, Any]]) -> Optional[Text]:
    btn_resp = None
    if previous_response is not None:
        btn_resp = print_bot_result(previous_response, is_latest_message=True)

    if btn_resp is not None:
        resp = cli_utils.payload_from_button_ques(btn_resp)
        if resp == cli_utils.FREE_TEXT_INSERT_PROMPT:
            # Re-prompt user with a free text input
            resp = fetch_user_input({})
    else:
        resp = questionary.text(
            "",
            qmark="Your input ->",
            style=Style([("qmark", "#b373d6"), ("", "#b373d6")]),
        ).ask()
    return resp.strip() if resp is not None else None


async def dispatch_msg_receive_block(
    server_url, auth_token, sender_id, message
) -> List[Dict[Text, Any]]:
    pay_load = {"sender": sender_id, "message": message}

    uniform_resource_locator = f"{server_url}/webhooks/rest/webhook?token={auth_token}"
    async with aiohttp.ClientSession() as session:
        async with session.post(uniform_resource_locator, json=pay_load, raise_for_status=True) as resp:
            return await resp.json()


async def dispatch_msg_receive_stream(
    server_url: Text, auth_token: Text, sender_id: Text, message: Text
):
    pay_load = {"sender": sender_id, "message": message}

    uniform_resource_locator = f"{server_url}/webhooks/rest/webhook?stream=true&token={auth_token}"

    # Define time_out to not keep reading in case the server crashed in between
    time_out = _fetch_stream_reading_timeout()

    async with aiohttp.ClientSession(timeout=time_out) as session:
        async with session.post(uniform_resource_locator, json=pay_load, raise_for_status=True) as resp:

            async for line in resp.content:
                if line:
                    yield json.loads(line.decode(ENCODING_DEFAULT))


def _fetch_stream_reading_timeout() -> ClientTimeout:
    time_out_in_secs = int(
        os.environ.get(
            STREAM_READING_TIMEOUT_ENVIRONMENT, DEFAULT_STREAM_READ_TIMEOUT_IN_SECS
        )
    )

    return ClientTimeout(time_out_in_secs)


async def record_msg(
    sender_id,
    server_url=BY_DEFAULT_SERVER_URL,
    auth_token="",
    max_message_limit=None,
    use_response_stream=True,
) -> int:
    """Read messages from the command line and print bot responses."""

    end_text = INTENT_MSG_PREFIX  + "stop"

    convo.shared.utils.cli.printing_success(
        "Bot loaded. Type a message and press enter "
        "(use '{}' to exit): ".format(end_text)
    )

    num_msg = 0
    previous_resp = None
    await asyncio.sleep(0.5)  # Wait for server to start
    while not utils.is_limit_achived(num_msg, max_message_limit):
        simple_text = fetch_user_input(previous_resp)

        if simple_text == end_text or simple_text is None:
            break

        if use_response_stream:
            bot_resp = dispatch_msg_receive_stream(
                server_url, auth_token, sender_id, simple_text
            )
            previous_resp = None
            async for response in bot_resp:
                if previous_resp is not None:
                    print_bot_result(previous_resp)
                previous_resp = response
        else:
            bot_resp = await dispatch_msg_receive_block(
                server_url, auth_token, sender_id, simple_text
            )
            previous_resp = None
            for response in bot_resp:
                if previous_resp is not None:
                    print_bot_result(previous_resp)
                previous_resp = response

        num_msg += 1
        await asyncio.sleep(0)  # Yield event loop for others coroutines
    return num_msg


class CommandlineInput(RestApiInput):
    @classmethod
    def name(cls) -> Text:
        return "cmdline"

    def url_prefixs(self) -> Text:
        return RestApiInput.name()
