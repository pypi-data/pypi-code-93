import asyncio
from typing import Text

import click

from neuralspace.apis import get_async_http_session
from neuralspace.ner.apis import get_ner_response
from neuralspace.ner.constants import SUPPORTED_LANGUAGES
from neuralspace.utils import setup_logger


@click.group(name="ner")
def ner():
    pass


@ner.command(
    name="parse",
)
@click.option(
    "-t",
    "--text",
    type=click.STRING,
    required=True,
    help="text to be parsed",
)
@click.option(
    "-L",
    "--language",
    type=click.STRING,
    required=True,
    help="language that the text was in",
)
@click.option(
    "-l", "--log-level", type=click.Choice(["INFO", "DEBUG", "ERROR"]), default="INFO"
)
def parse(text: Text, language: Text, log_level: Text):
    setup_logger(log_level=log_level)
    if not language:
        ValueError(f"Language is mandatory. You can select from {SUPPORTED_LANGUAGES}")
    if not text:
        ValueError("Please enter the text to parse")
    loop = asyncio.new_event_loop()
    loop.run_until_complete(get_ner_response(text, language))
    loop.run_until_complete(get_async_http_session().close())
