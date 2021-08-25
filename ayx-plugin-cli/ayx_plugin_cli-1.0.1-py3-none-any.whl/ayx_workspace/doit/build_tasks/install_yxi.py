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
"""Task definition for installing YXIs into Alteryx Designer."""
import os
from pathlib import Path
from typing import Dict
from zipfile import ZipFile

from ayx_plugin_cli.ayx_workspace.constants import YXI_OUTPUT_DIR


def task_install_yxi() -> Dict:
    """Install a YXI from a specified path, into a specified location."""
    # TODO: Make sure to prompt the user to restart designer on any changes to config
    return {
        "actions": [(unzip_yxi,)],
        "clean": True,
        "params": [
            {
                "name": "yxi_path",
                "long": "yxi_path",
                "type": Path,
                "default": YXI_OUTPUT_DIR / "main.yxi",
            },
            {
                "name": "install_dir",
                "long": "install_dir",
                "type": Path,
                "default": Path(os.environ.get("APPDATA", ".")) / "Alteryx" / "Tools",
            },
        ],
    }


def unzip_yxi(yxi_path: Path, install_dir: Path) -> None:
    """Copy tool subdirectories from the specified yxi into the target directory."""
    if not yxi_path.is_file():
        raise FileNotFoundError(
            f"Cannot unzip nonexistent yxi, check {yxi_path.resolve()}"
        )

    install_dir.mkdir(parents=True, exist_ok=True)

    with ZipFile(yxi_path, "r") as yxi:
        tool_names = [
            compressed_object.filename[:-1]
            for compressed_object in yxi.filelist
            if compressed_object.is_dir()
        ]
        files = [
            file_name
            for file_name in yxi.namelist()
            if Path(file_name).parts[0] in tool_names
        ]
        yxi.extractall(path=install_dir, members=files)
