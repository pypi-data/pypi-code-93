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
"""Validation helper methods."""
from typing import Callable, List, TYPE_CHECKING, Type, Union

from ayx_plugin_cli.node_js_helpers import run_node_js, run_npm

from packaging import version

if TYPE_CHECKING:
    import subprocess  # noqa: F401


class NodeJsNotFoundError(Exception):
    """NodeJS not found error."""

    pass


class NodeJsVersionError(Exception):
    """NodeJS Version error."""

    def __init__(self, min_version: str, bad_version: str):
        """Create a NodeJsVersionError."""
        self.min_version = min_version
        self.bad_version = bad_version


class NpmNotFoundError(NodeJsNotFoundError):
    """NPM not found error."""

    pass


class NpmVersionError(NodeJsVersionError):
    """NPM Version Error."""

    pass


def validate_node_js(
    min_version: Union[version.LegacyVersion, version.Version]
) -> None:
    """Validate that node is installed with a minimum version."""
    _validate_js_package(
        run_node_js, min_version, NodeJsNotFoundError, NodeJsVersionError
    )


def validate_npm(min_version: Union[version.LegacyVersion, version.Version]) -> None:
    """Validate that npm is installed with a minimum version."""
    _validate_js_package(run_npm, min_version, NpmNotFoundError, NpmVersionError)


def _validate_js_package(
    runner: Callable[[List[str]], "subprocess.CompletedProcess"],
    min_version: Union[version.LegacyVersion, version.Version],
    not_found_error: Type[NodeJsNotFoundError],
    version_error: Type[NodeJsVersionError],
) -> None:
    """Validate that JS packages are all available."""
    try:
        completed_process = runner(["--version"])
    except Exception:
        raise not_found_error()

    if completed_process.returncode != 0:
        raise not_found_error()

    package_version = version.parse(completed_process.stdout.decode("utf-8"))

    if package_version < min_version:
        raise version_error(str(min_version), str(package_version))
