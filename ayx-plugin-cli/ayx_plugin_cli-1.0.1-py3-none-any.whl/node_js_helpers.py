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
"""Helper methods for running Node JS."""
import subprocess
from typing import Any, List


def run_node_js(args: List[str], **kwargs: Any) -> subprocess.CompletedProcess:
    """Run a node subprocess."""
    return _run_node_subprocess(["node"] + args, **kwargs)


def run_npm(args: List[str], **kwargs: Any) -> subprocess.CompletedProcess:
    """Run an NPM subprocess."""
    return _run_node_subprocess(["npm"] + args, **kwargs)


def _run_node_subprocess(args: List[str], **kwargs: Any) -> subprocess.CompletedProcess:
    """Run a node js subprocess."""
    # We have to use `shell=True` here because node/npm frequently use nested environment
    # variables to resolve their install locations, which is a feature that is only present
    # with shell=True. As a result, it is recommended to use a single string as the command
    # instead of a list of string arguments, which is why we join them here.
    return subprocess.run(" ".join(args), capture_output=True, shell=True, **kwargs)
