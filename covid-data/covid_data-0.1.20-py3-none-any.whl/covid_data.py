#!/usr/bin/env python
import os
from importlib import import_module

import click
from dotenv import load_dotenv

from covid_data.logger import init_logger

load_dotenv()

init_logger()


@click.group()
def cli():
    pass


def entrypoint():
    base_path = os.path.join(os.path.dirname(__file__), "commands")
    files = os.listdir(base_path)

    for file_name in files:
        if (
            file_name.startswith("test")
            or file_name.startswith("__")
            or os.path.isdir(os.path.join(base_path, file_name))
        ):
            continue

        handler_module, _ = os.path.splitext(file_name)

        module = import_module(f".{handler_module}", "covid_data.commands")

        if not hasattr(module, "main"):
            continue

        cli.add_command(module.main)  # type: ignore

    cli()
