# Copyright (C) 2021 Alteryx, Inc. All rights reserved.
#
# Licensed under the ALTERYX SDK AND API LICENSE AGREEMENT;
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.alteryx.com/alteryx-sdk-and-api-license-agreement
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""A module to check pypi or artifactory for CLI updates."""
from typing import Dict, List
from xml.etree import ElementTree

from ayx_plugin_cli.ayx_workspace.constants import PYPI_URL
from ayx_plugin_cli.version import version

import packaging

import requests

import typer


class UpdateChecker:
    """A class to check artifactory or pypi for updates."""

    url = PYPI_URL
    version = version

    @staticmethod
    def _get_all_builds(content: str) -> List[str]:
        """Pull a list of all available ayx_cli builds from artifactory."""
        tree = ElementTree.fromstring(content)

        return list(
            sorted(
                [a.text.split("-")[1] for a in tree.iter("a") if a.text is not None],
                key=packaging.version.parse,
            )
        )

    @staticmethod
    def _get_most_recent_version_from_json(pypi_json: Dict[str, Dict[str, str]]) -> str:
        """Return the most recent ayx_cli version."""
        return pypi_json["info"]["version"]

    @classmethod
    def _get_most_recent_version_from_xml(cls, content: str) -> str:
        sorted_versions = cls._get_all_builds(content)
        return sorted_versions[-1]

    @classmethod
    def check_for_updates(cls) -> None:
        """Check to see if there's a more recent version of AyxPythonSdk available."""
        try:
            versions_page = requests.get(cls.url, timeout=10)
            versions_page.raise_for_status()
            if "pypi.org" in cls.url:
                most_recent_version = cls._get_most_recent_version_from_json(
                    versions_page.json()
                )
            else:
                most_recent_version = cls._get_most_recent_version_from_xml(
                    versions_page.content.decode(versions_page.encoding)
                )
        except (
            AttributeError,
            ValueError,
            requests.ConnectionError,
            requests.HTTPError,
            requests.Timeout,
        ):
            typer.echo(f"Can't retrieve version info from {cls.url}")
            return
        if packaging.version.parse(cls.version) < packaging.version.parse(
            most_recent_version
        ):
            typer.echo(
                f"WARNING: You are using ayx_plugin_cli version {cls.version} - Version {most_recent_version} is available"
            )
