import re
from pathlib import Path

import respx
from decouple import config
from httpx import Response

from onlineafspraken.api.client import client


def get_response(method: str) -> str:
    file_path = Path(__file__).parent / "responses" / str(method + ".xml")

    return file_path.read_text()


def save_response(method, data):

    file_path = Path(__file__).parent / "responses" / str(method + ".xml")

    if len(data) > 0:
        file_path.write_bytes(data)


@respx.mock
def mock_request(method: str):

    if config('SAVE_RESPONSE', default=False, cast=bool) is False:

        url = client.get_base_url()

        rx = re.compile(rf"{url}*")

        respx.get(url=rx).mock(return_value=Response(200, text=get_response(method)))
    else:
        respx.stop()
