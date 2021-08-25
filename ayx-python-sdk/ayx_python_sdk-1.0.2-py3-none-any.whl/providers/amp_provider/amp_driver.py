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
"""AMP Driver class definition."""
import logging
import traceback
from typing import Any, Callable, Optional

from ayx_python_sdk.core import Plugin
from ayx_python_sdk.core.exceptions import WorkflowRuntimeError
from ayx_python_sdk.core.input_connection_base import InputConnectionStatus
from ayx_python_sdk.providers.amp_provider.repositories import (
    IORepository,
    InputConnectionRepository,
    InputRecordPacketRepository,
    LoggerRepository,
    Singleton,
)
from ayx_python_sdk.providers.amp_provider.repositories.input_record_packet_repository import (
    EmptyRecordPacketRepositoryException,
    UnfinishedRecordPacketException,
)

logger = logging.getLogger(__name__)


class AMPDriver(metaclass=Singleton):
    """The AMP Driver is a class that manages the lifecycle methods of a plugin instance."""

    def __init__(self) -> None:
        self.__plugin: Optional["Plugin"] = None

    @staticmethod
    def _handle_workflow_error(exception: WorkflowRuntimeError) -> None:
        traceback_list = traceback.format_tb(exception.__traceback__)
        traceback_string = "".join(["\n"] + traceback_list[1:])
        IORepository().save_error(traceback_string)

    @staticmethod
    def _handle_all_errors(exception: Exception) -> None:
        traceback_list = traceback.format_tb(exception.__traceback__)
        traceback_string = "".join(["\n"] + traceback_list[1:])
        amp_logger = LoggerRepository().get_logger()
        IORepository().save_error(
            f"Unexpected error in plugin, refer to {LoggerRepository().get_log_file()}"
        )
        amp_logger.exception(traceback_string)

    def _run_with_error_handling(self, _callable: Callable, *args: Any) -> None:
        try:
            _callable(*args)
        except WorkflowRuntimeError as e:
            IORepository.save_error(f"WorkflowRuntimeError: {e}")
        except Exception as e:
            self._handle_all_errors(e)

    def metadata_received(self, anchor_name: str, connection_name: str) -> None:
        """
        Retrieve the input connection, and call plugin's on_input_connection_initialized method.

        Parameters
        ----------
        anchor_name: str
            The name of the input anchor associated with the connection to be initialized.

        connection_name: str
            The name of the input connection to be retrieved.
        """
        connection = InputConnectionRepository().get_connection(
            anchor_name, connection_name
        )

        InputConnectionRepository().save_connection_status(
            anchor_name, connection_name, InputConnectionStatus.INITIALIZED
        )
        logger.debug(f"Connection {connection_name} on {anchor_name} initialized")
        self._run_with_error_handling(
            self.plugin.on_input_connection_opened, connection
        )

    def record_packet_received(self, anchor_name: str, connection_name: str) -> None:
        """
        Retrieve input connection, and call plugin's on_record_packet method.

        Parameters
        ----------
        anchor_name: str
            The name of the input anchor associated with the connection to be read from.

        connection_name: str
            The name of the input connection to be retrieved.
        """
        connection = InputConnectionRepository().get_connection(
            anchor_name, connection_name
        )
        InputConnectionRepository().save_connection_status(
            anchor_name, connection_name, InputConnectionStatus.RECEIVING_RECORDS
        )
        logger.debug(
            f"Connection {connection_name} on anchor {anchor_name} receiving records"
        )
        while True:
            try:
                InputRecordPacketRepository().peek_record_packet(
                    anchor_name, connection_name
                )
            except (
                UnfinishedRecordPacketException,
                EmptyRecordPacketRepositoryException,
            ):
                break
            else:
                logger.debug(
                    f"Sending record packet to connection {connection_name} on anchor {anchor_name}"
                )
                self._run_with_error_handling(self.plugin.on_record_packet, connection)
                InputRecordPacketRepository().pop_record_packet(
                    anchor_name, connection_name
                )

    def connection_closed_callback(
        self, anchor_name: str, connection_name: str
    ) -> None:
        """
        Close individual connections.

        Parameters
        ----------
        anchor_name: str
            The name of the input anchor associated with the connection to be closed.

        connection_name: str
            The name of the input connection to be closed.
        """
        InputConnectionRepository().save_connection_status(
            anchor_name, connection_name, InputConnectionStatus.CLOSED
        )
        logger.debug(f"Closed connection {connection_name} on anchor {anchor_name}")
        try:
            InputRecordPacketRepository().peek_record_packet(
                anchor_name, connection_name
            )
        except EmptyRecordPacketRepositoryException:
            pass
        except ValueError:
            logger.debug(
                f"{anchor_name} was not found in the InputRecordPacketRepository. (There were no records associated with this anchor.)"
            )
        else:
            self._run_with_error_handling(
                self.plugin.on_record_packet,
                InputConnectionRepository().get_connection(
                    anchor_name, connection_name
                ),
            )

    def complete_callback(self) -> None:
        """Call plugin's on_complete method."""
        logger.debug(f"Plugin complete, closing")
        self._run_with_error_handling(self.plugin.on_complete)

    @property
    def plugin(self) -> "Plugin":
        """
        Get the plugin associated with this driver.

        Returns
        -------
        Plugin
            The plugin associated with this AMP Driver instance.

        Raises
        ------
        ValueError
            If the plugin hasn't been assigned.
        """
        if self.__plugin is None:
            raise ValueError("Plugin has not been initialized")
        return self.__plugin

    @plugin.setter
    def plugin(self, value: "Plugin") -> None:
        """
        Set the plugin associated with this driver.

        Parameters
        ----------
        value: Plugin
            The plugin to be assigned.

        """
        self.__plugin = value
        logger.debug(f"Assigned plugin {value}")

    def clear_state(self) -> None:
        """Reset the AMP Driver."""
        self.__plugin = None
