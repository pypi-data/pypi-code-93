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
"""AMP SDK Plugin Proxy class."""
import logging
import os
import sys
from logging import Logger
from pathlib import Path
from typing import Optional, Tuple

from ayx_python_sdk.providers.amp_provider.repositories.singleton import Singleton


class LoggerRepository(metaclass=Singleton):
    """Class that encapsulates attributes shared between AMPProvider and AMPDriver."""

    def __init__(self) -> None:
        self.__logger_name: Optional[str] = None
        self.__log_file: Optional[Path] = None

    def _configure_logging(self) -> Tuple[Path, str]:
        from ayx_python_sdk.providers.amp_provider import (
            AMPDriver,
            AMPEnvironment,
        )

        plugin_name: str = AMPDriver().plugin.__class__.__name__
        logger_name = f"{plugin_name}.{AMPEnvironment().tool_id}"
        log_directory = (
            Path(os.environ["localappdata"]) / "Alteryx"
            if sys.platform == "win32"
            else Path.home() / ".Alteryx"
        ) / "Log"
        log_directory.mkdir(parents=True, exist_ok=True)
        log_file = log_directory / f"{logger_name}.log"

        logger = logging.getLogger(logger_name)
        handler = logging.FileHandler(log_file)

        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        _level = (
            logging.DEBUG if os.environ.get("AYX_SDK_VERBOSE", False) else logging.INFO
        )
        logger.setLevel(_level)
        return log_file, logger_name

    def get_log_file(self) -> Path:
        """Retrieve the path to the plugin's logfile."""
        if self.__log_file is None:
            self.__log_file, self.__logger_name = self._configure_logging()
        return self.__log_file

    def get_logger(self) -> "Logger":  # noqa: D102
        """Retrieve the plugin's logger."""
        if self.__logger_name is None:
            self.__log_file, self.__logger_name = self._configure_logging()
        return logging.getLogger(self.__logger_name)

    def clear_repository(self) -> None:
        """Clear the AMP Plugin proxy's state."""
        self.__logger_name = None
        self.__log_file = None
