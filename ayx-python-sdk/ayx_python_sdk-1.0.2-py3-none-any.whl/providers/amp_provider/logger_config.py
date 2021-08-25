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
"""Logger configuration utilities."""
import logging
import os
from pathlib import Path


def configure_logger() -> None:
    """Configure the logger for the Python SDK."""
    logging.raiseExceptions = False
    env_dir = os.environ.get("LOCALAPPDATA") or os.environ.get("HOME")
    if env_dir is None:
        raise ValueError(
            "LOCALAPPDATA or HOME environment variables should be set for logging."
        )
    log_dir = Path(env_dir) / "Alteryx" / "Log"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "PythonSDK.log"

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # TODO: Figure how to make python not choke on full stdout buffer
    # stream_handler = logging.StreamHandler(sys.stdout)
    # stream_handler.setFormatter(formatter)
    # logger.addHandler(stream_handler)
