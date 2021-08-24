from __future__ import annotations

import click
import httpx

from pkg_resources import parse_requirements
from pkg_resources import parse_version
from pkg_resources import Requirement

from pipwhip.utils import coro


@click.command()
@coro
@click.option(
    "-r",
    "--requirement",
    type=click.Path(),
)
async def pipwhip(requirement: str) -> None:
    await execute(requirement)


async def get_versions(package_name: str) -> tuple[str, list[str]]:
    async with httpx.AsyncClient() as client:
        request = await client.get(f"https://pypi.org/pypi/{package_name}/json")

    _version = request.json()["releases"]
    _name = request.json()["info"]["name"]
    _sorted_version = sorted(_version, key=parse_version, reverse=True)
    return _name, _sorted_version


def file_parse(requirements_file: str) -> list[Requirement]:
    with open(requirements_file) as requirements_txt:
        return [requirement for requirement in parse_requirements(requirements_txt)]


def update_txt_file(requirements_file: str, package: str, version: str) -> None:
    with open(requirements_file, "a") as f:
        f.write(f"{package}=={version}")
        f.write("\n")


def erase_file_contents(requirements_file: str) -> None:
    with open(requirements_file, "r+") as f:
        f.truncate(0)
        f.close()


async def execute(requirements_file: str) -> None:
    parsed_file = file_parse(requirements_file)
    erase_file_contents(requirements_file)
    for package in parsed_file:
        result = await get_versions(package.name)  # type: ignore
        latest_version = result[1][0]
        update_txt_file(requirements_file, result[0], latest_version)
