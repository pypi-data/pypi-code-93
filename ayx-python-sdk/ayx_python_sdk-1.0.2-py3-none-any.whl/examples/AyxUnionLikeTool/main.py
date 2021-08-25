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
"""Example union tool."""
from ayx_python_sdk.core import (
    InputConnectionBase,
    Plugin,
    ProviderBase,
    register_plugin,
)
from ayx_python_sdk.core.exceptions import WorkflowRuntimeError


class AyxUnionLikeTool(Plugin):
    """A sample Plugin that performs a union operation on data from multiple input connections and writes to a single output anchor."""

    def __init__(self, provider: ProviderBase):
        """Construct the AyxRecordProcessor."""
        self.provider = provider
        self.output_anchor = self.provider.get_output_anchor("Output")
        self.all_dataframes = []
        self.first_connection = None
        self.provider.io.info("Union-Like tool started")

    def on_input_connection_opened(self, input_connection: InputConnectionBase) -> None:
        """Initialize the Input Connections of this plugin."""
        if input_connection.metadata is None:
            raise RuntimeError("Metadata must be set before setting containers.")
        input_connection.max_packet_size = 100

        if self.first_connection is None:
            self.first_connection = input_connection
            output_metadata = input_connection.metadata.clone()
            self.output_anchor.open(output_metadata)

        if self.first_connection.metadata != input_connection.metadata:
            raise WorkflowRuntimeError(
                f"Metadata does not match for connections {self.first_connection.name} and {input_connection.name}:\n{self.first_connection.metadata} != {input_connection.metadata}"
            )

    def on_record_packet(self, input_connection: InputConnectionBase) -> None:
        """Handle the record packet received through the input connection."""
        packet = input_connection.read()
        self.output_anchor.write(packet)

    def on_complete(self) -> None:
        """Handle for when the plugin is complete."""
        self.provider.io.info("Union-Like tool done")


AyxPlugin = register_plugin(AyxUnionLikeTool)
