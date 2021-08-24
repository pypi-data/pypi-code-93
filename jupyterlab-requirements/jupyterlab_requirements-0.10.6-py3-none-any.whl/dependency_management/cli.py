#!/usr/bin/env python3
# thoth-storages
# Copyright(C) 2021 Francesco Murdaca
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""A CLI to jupyterlab-requirements library."""

import logging
import os

import click
from typing import Optional
from pathlib import Path

_LOGGER = logging.getLogger("thoth.jupyterlab_requirements.cli")


def _get_version(name):
    """Print jupyterlab-requirements version and exit."""
    with open(os.path.join(name, "__init__.py")) as f:
        content = f.readlines()

    for line in content:
        if line.startswith("__version__ ="):
            # dirty, remove trailing and leading chars
            return line.split(" = ")[1][1:-2]
    raise ValueError("No version identifier found")

def _print_version(ctx: click.Context, _, value: str):
    """Print version and exit."""
    if not value or ctx.resilient_parsing:
        return

    click.echo(_get_version(name="jupyterlab_requirements"))
    ctx.exit()

# @click.option(
#     "-v",
#     "--verbose",
#     is_flag=True,
#     envvar="JUPYTERLAB_REQUIREMENTS_VERBOSE",
#     help="Be verbose about what's going on.",
# )
# @click.option(
#     "--version",
#     is_flag=True,
#     help="Print output in JSON format."
# )
# def cli(
#     verbose: bool = False,
#     version: bool = False,
# ):
#     """CLI tool for jupyterlab-requirements."""
#     if verbose:
#         _LOGGER.setLevel(logging.DEBUG)
#         _LOGGER.debug("Debug mode turned on")
#         _LOGGER.debug("Jupyterlab-requirements version: %r", _get_version(name="jupyterlab_requirements"))

#     if version:
#         version_library = _get_version(name="jupyterlab_requirements")
#         click.echo(version_library)


@click.command()
@click.pass_context
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    envvar="THOTH_SOLVER_PROJECT_URL_DEBUG",
    help="Be verbose about what's going on.",
)
@click.option(
    "--version",
    is_flag=True,
    is_eager=True,
    callback=_print_version,
    expose_value=False,
    help="Print version and exit.",
)
# @click.option(
#     "--start-date",
#     envvar="THOTH_GET_SOURCE_REPOS_START_DATE",
#     help="Use solver results starting the given date.",
#     metavar="YYYY-MM-DD",
#     type=str,
# )
# @click.option(
#     "--end-date",
#     help="Upper bound for solver results listing.",
#     metavar="YYYY-MM-DD",
#     envvar="THOTH_GET_SOURCE_REPOS_END_DATE",
#     type=str,
# )
# @click.option(
#     "--output",
#     help="Store result to a file or print to stdout (-).",
#     metavar="FILE",
#     envvar="THOTH_GET_SOURCE_REPOS_OUTPUT",
#     type=str,
# )
def cli(
    _: click.Context,
    verbose: bool = False,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    output: Optional[str] = None,
):
    """Aggregate Github URLs for GitHub hosted projects on PyPI."""
    if verbose:
        _LOGGER.setLevel(logging.DEBUG)

    _LOGGER.debug("Debug mode is on")
    _LOGGER.info("Version: %s", _get_version(name="jupyterlab_requirements"))

    # start_date_converted = None
    # if start_date:
    #     start_date_converted = datetime.strptime(start_date, _DATE_FORMAT).date()

    # end_date_converted = None
    # if end_date:
    #     end_date_converted = datetime.strptime(end_date, _DATE_FORMAT).date()

    # urls = get_source_repos(start_date=start_date_converted, end_date=end_date_converted)

    # if output == "-" or not output:
    #     yaml.safe_dump(urls, sys.stdout)
    # else:
    #     _LOGGER.info("Writing results computed to %r", output)
    #     with open(output, "w") as f:
    #         yaml.safe_dump(urls, f)


__name__ == "__main__" and cli()