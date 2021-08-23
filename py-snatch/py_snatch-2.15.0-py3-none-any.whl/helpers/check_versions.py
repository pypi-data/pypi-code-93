"""Version package.

Checks version number for upgrades in PyPI
"""
from functools import lru_cache
from typing import List, Optional

import arrow
import requests
from loguru import logger
from pkg_resources import parse_version
from requests import RequestException


@lru_cache
def get_pypi_versions(time) -> Optional[List[str]]:
    """Return the version list data from PyPI.

    :return: list
    """
    url = "https://pypi.python.org/pypi/py-snatch/json"
    versions_list = None
    try:
        ret = requests.get(url, timeout=1)
        data = ret.json()
    except RequestException:
        return None
    if data:
        versions_list = list(data["releases"].keys())
        versions_list.sort(key=parse_version)
    return versions_list


def check_versions(verbose: bool = False) -> None:
    """Check if it is the latest version.

    Compares actual version vs last known
    version in PyPI, for upgrades

    :return:
        string
    """
    from snatch import __version__

    last_version = __version__
    if verbose:
        logger.info(f"Checking for latest version. Current version is: {__version__}")

    now = arrow.utcnow().ceil("hour").timestamp()
    all_versions = get_pypi_versions(now)
    if all_versions:
        last_version = all_versions[-1]
    if parse_version(last_version) > parse_version(__version__) and (
        "rc" not in last_version
        and "b" not in last_version
        and "dev" not in last_version
    ):
        logger.warning(
            f"You're running a outdated version. "
            f"Last Version: {last_version} - Please update."
        )
    elif verbose:
        logger.success("Success: You're using the latest version.")
