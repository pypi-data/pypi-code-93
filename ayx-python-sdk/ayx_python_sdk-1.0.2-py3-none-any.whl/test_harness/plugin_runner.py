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
"""Class for running a plugin out of process."""
import os
import sys
import tempfile
import time
from concurrent import futures
from enum import Enum
from pathlib import Path
from typing import Callable, List, Optional, TYPE_CHECKING, Tuple

from ayx_python_sdk.providers.amp_provider import (
    AMPInputAnchor,
    AMPInputConnection,
    AMPOutputAnchor,
    AMPRecordPacket,
)
from ayx_python_sdk.providers.amp_provider.builders import OutputAnchorBuilder
from ayx_python_sdk.providers.amp_provider.builders import RecordPacketBuilder
from ayx_python_sdk.providers.amp_provider.builders.input_anchor_builder import (
    InputAnchorBuilder,
)
from ayx_python_sdk.providers.amp_provider.grpc_util import SocketAddress
from ayx_python_sdk.providers.amp_provider.repositories.test_harness_state_repository import (
    TestHarnessStateRepository,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.incoming_connection_complete_pb2 import (
    IncomingConnectionComplete,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.incoming_record_packet_push_pb2 import (
    IncomingRecordPacketPush,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.plugin_initialization_data_pb2 import (
    PluginInitializationData,
    UpdateMode,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.sdk_engine_service_pb2_grpc import (
    add_SdkEngineServicer_to_server,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.sdk_tool_service_pb2_grpc import (
    SdkToolStub,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.transport_pb2 import (
    Empty,
)
from ayx_python_sdk.test_harness.process_lifecycle_manager import (
    ProcessLifecycleManager,
)
from ayx_python_sdk.test_harness.sdk_engine_service import SdkEngineService

import grpc

import typer

import xmltodict

if TYPE_CHECKING:
    from ayx_python_sdk.core import Metadata  # noqa: F401
    import pandas as pd  # noqa: F401


class RunMode(str, Enum):
    """Run mode types."""

    update_only = "update_only"
    full_run = "full"


def _handle_sdk_tool_service_exception(method: Callable) -> Callable:
    def _log_grpc_errors(*args, **kwargs):  # type: ignore
        try:
            return method(*args, **kwargs)
        except grpc.RpcError as e:
            typer.echo("SDK Tool Service failed.")
            typer.echo(f"gRPC Status Code: {e.code()}")
            typer.echo(f"gRPC Details (Stacktrace):\n{e.details()}")
            raise typer.Exit(code=1)

    return _log_grpc_errors


def _parse_config_xml(
    xml_path: Path,
) -> Tuple[List[AMPInputAnchor], List[AMPOutputAnchor]]:
    input_anchors = []
    output_anchors = []
    with open(xml_path) as config_xml:
        config_dict = xmltodict.parse(config_xml.read())
        inputs = config_dict["AlteryxJavaScriptPlugin"]["GuiSettings"][
            "InputConnections"
        ]["Connection"]
        outputs = config_dict["AlteryxJavaScriptPlugin"]["GuiSettings"][
            "OutputConnections"
        ]["Connection"]
        if type(inputs) is list:
            for input_anchor in inputs:
                anchor = AMPInputAnchor(
                    name=input_anchor["@Name"],
                    allow_multiple=input_anchor["@AllowMultiple"],
                    optional=input_anchor["@Optional"],
                )
                input_anchors.append(anchor)
        else:
            anchor = AMPInputAnchor(
                name=inputs["@Name"],
                allow_multiple=inputs["@AllowMultiple"],
                optional=inputs["@Optional"],
            )
            input_anchors.append(anchor)

        if type(outputs) is list:
            for output_anchor in outputs:
                anchor = AMPOutputAnchor(
                    name=output_anchor["@Name"],
                    allow_multiple=output_anchor["@AllowMultiple"],
                    optional=output_anchor["@Optional"],
                )
                output_anchors.append(anchor)
        else:
            anchor = AMPOutputAnchor(
                name=outputs["@Name"],
                allow_multiple=outputs["@AllowMultiple"],
                optional=outputs["@Optional"],
            )
            output_anchors.append(anchor)

    return input_anchors, output_anchors


class PluginRunner:
    """Class for running a plugin out of process with test data."""

    def __init__(
        self,
        plugin_entrypoint: Path,
        plugins_package: str,
        tool_name: str,
        input_metadata: List["Metadata"],
        input_data: List["pd.DataFrame"],
        config_xml: Path,
    ) -> None:
        """Construct the plugin runner."""
        self._plugin_entrypoint = plugin_entrypoint
        self._plugins_package = plugins_package
        self._tool_name = tool_name
        self._input_metadata = input_metadata
        self._input_data = input_data
        self._sdk_engine_server, self._sdk_engine_server_address = self._build_sdk_engine_server()  # type: ignore
        self._sdk_tool_client: Optional[SdkToolStub] = None
        self._input_anchors, self._output_anchors = _parse_config_xml(config_xml)
        for i in range(len(self._input_anchors)):
            connection = [
                AMPInputConnection(
                    "Connection" + str(i),
                    metadata=self._input_metadata[i],
                    anchor=self._input_anchors[i],
                )
            ]
            self._input_anchors[i].connections.extend(connection)

        if not (
            len(self._input_data)
            == len(self._input_anchors)
            == len(self._input_metadata)
        ):
            raise Exception(
                "Input datasets, input metadata, and input anchors must match."
            )

    def run_plugin(self, mode: RunMode) -> None:
        """Run the plugin out of process."""
        self._sdk_engine_server.start()
        with ProcessLifecycleManager(
            [
                sys.executable,
                str(self._plugin_entrypoint.resolve()),
                "start-sdk-tool-service",
                self._plugins_package,
                self._tool_name,
                "--sdk-engine-server-address",
                self._sdk_engine_server_address.address,
            ]
        ) as plugin_process:  # noqa: F841
            self._wait_for_handshake(plugin_process)
            self._sdk_tool_client = self._build_sdk_tool_client(
                TestHarnessStateRepository().get_sdk_tool_server_address()
            )

            self._run_handshake()
            self._initialize_plugin()

            if mode == RunMode.full_run:
                self._send_input_record_packets()
                self._complete_connection()
                self._close_plugin()

    @_handle_sdk_tool_service_exception
    def _run_handshake(self) -> None:
        """Run the handshake with the SDK tool service."""
        if self._sdk_tool_client is None:
            raise ValueError("SDK Tool Client must be set.")

        return_status = self._sdk_tool_client.ConfirmSdkToolServiceConnection(Empty())
        typer.echo(
            f"SDK TOOL CLIENT: Sdk Tool Service ran successfully with return value\n{return_status}"
        )

    def get_output_data(self) -> List["pd.DataFrame"]:
        """Get the output data from the plugin."""
        output_data = []
        for out in self._output_anchors:
            out_df = (
                TestHarnessStateRepository().get_record_packet(out.name).to_dataframe()
            )
            output_data.append(out_df)
        return output_data

    def get_output_metadata(self) -> List["Metadata"]:
        """Get the output metadata from the plugin."""
        output_metadata = []
        for out in self._output_anchors:
            out_metadata = TestHarnessStateRepository().get_metadata(out.name)
            output_metadata.append(out_metadata)
        return output_metadata

    @staticmethod
    def _wait_for_handshake(
        plugin_process: ProcessLifecycleManager, timeout: float = 30.0
    ) -> None:
        """Wait for the initialization handshake to complete."""
        start = time.time()
        while not TestHarnessStateRepository().get_handshake_completed_status():
            # Yield to server threads to allow processing of handshake
            time.sleep(0.01)

            if not plugin_process.process_alive():
                typer.echo(
                    f"ERROR: Plugin process died before handshake completed with error."
                )
                raise typer.Exit(code=1)

            if time.time() - start > timeout:
                typer.echo("ERROR: Handshake didn't complete within timeout.")
                raise typer.Exit(code=1)

    @_handle_sdk_tool_service_exception
    def _initialize_plugin(self) -> None:
        """Initialize the plugin with metadata and configuration."""
        temp_dir = tempfile.TemporaryDirectory()
        dummy_plugin_data = PluginInitializationData(
            configXml="<Configuration />",
            incomingAnchors=[
                InputAnchorBuilder.to_protobuf(input_anchor)
                for input_anchor in self._input_anchors
            ],
            outgoingAnchors=[
                OutputAnchorBuilder.to_protobuf(output_anchor)
                for output_anchor in self._output_anchors
            ],
            engineConstants={
                "Engine.TempFilePath": temp_dir.name,
                "Engine.WorkflowDirectory": os.getcwd(),
                "Engine.Version": "0.0.0.0",
                "AlteryxExecutable": os.getcwd(),
                "ProxyConfiguration": "ProxyRequiresCredentials=false\nProxyCommonUserName=\nProxyCommonPassword=\n",
            },
            updateMode=UpdateMode.UM_Run,
        )

        if self._sdk_tool_client is None:
            raise ValueError("SDK Tool Client must be set.")

        typer.echo(
            f"SDK TOOL CLIENT: Initialization Completed\n{self._sdk_tool_client.InitializeSdkPlugin(dummy_plugin_data)}"
        )

    @_handle_sdk_tool_service_exception
    def _send_input_record_packets(self) -> None:
        """Send all of the record packets to the plugin."""
        for i in range(len(self._input_anchors)):
            dummy_record_packets = RecordPacketBuilder().to_protobuf(
                amp_record_packet=AMPRecordPacket(
                    self._input_metadata[i], self._input_data[i]
                ),
                sequence=0,
                progress=0.0,
            )

            if self._sdk_tool_client is None:
                raise ValueError("SDK Tool Client must be set.")
            for record_packet in dummy_record_packets:
                dummy_record_packet_push = IncomingRecordPacketPush(
                    anchor_name=self._input_anchors[i].name,
                    connection_name=self._input_anchors[i].connections[0].name,
                    record_packet=record_packet,
                )
                typer.echo(
                    f"SDK TOOL CLIENT: {self._input_anchors[i].name} Record Packet(s) Pushed\n{self._sdk_tool_client.PushIncomingRecordPacket(dummy_record_packet_push)}"
                )

    @_handle_sdk_tool_service_exception
    def _complete_connection(self) -> None:
        for i in range(len(self._input_anchors)):
            incoming_connection_complete = IncomingConnectionComplete(
                anchor_name=self._input_anchors[i].name,
                connection_name=self._input_anchors[i].connections[0].name,
            )

            if self._sdk_tool_client is None:
                raise ValueError("SDK Tool Client must be set.")

            typer.echo(
                f"SDK TOOL CLIENT: Connection Complete\n{self._sdk_tool_client.NotifyIncomingConnectionComplete(incoming_connection_complete)}"
            )

    @_handle_sdk_tool_service_exception
    def _close_plugin(self) -> None:
        if self._sdk_tool_client is None:
            raise ValueError("SDK Tool Client must be set.")

        typer.echo(
            f"SDK TOOL CLIENT: Plugin closed\n{self._sdk_tool_client.NotifyPluginComplete(Empty())}"
        )

    @staticmethod
    def _build_sdk_engine_server():  # type: ignore
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        add_SdkEngineServicer_to_server(SdkEngineService(), server)
        port = server.add_insecure_port("localhost:0")
        return server, SocketAddress("localhost", port)

    @staticmethod
    def _build_sdk_tool_client(address: SocketAddress) -> SdkToolStub:
        channel = grpc.insecure_channel(address.address)
        client = SdkToolStub(channel)
        return client
