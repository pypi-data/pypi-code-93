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
"""Example multiple input anchor tool."""
from ayx_python_sdk.core import (
    InputConnectionBase,
    Plugin,
    ProviderBase,
    register_plugin,
)
from ayx_python_sdk.core.exceptions import WorkflowRuntimeError


class AyxSdkMultipleInputAnchors(Plugin):
    """Concrete implementation of an AyxPlugin."""

    def __init__(self, provider: ProviderBase) -> None:
        """Construct a plugin."""
        self.provider = provider
        self.output_anchor = self.provider.get_output_anchor("Output")

        self.provider.io.info("Plugin initialized.")

    def on_input_connection_opened(self, input_connection: InputConnectionBase) -> None:
        """Initialize the Input Connections of this plugin."""
        if not self.output_anchor.is_open:
            self.output_anchor.open(input_connection.metadata)

        incoming_names = [field.name for field in input_connection.metadata]
        incoming_types = [field.type for field in input_connection.metadata]

        outgoing_names = [field.name for field in self.output_anchor.metadata]
        outgoing_types = [field.type for field in self.output_anchor.metadata]

        if incoming_names != outgoing_names or incoming_types != outgoing_types:
            raise WorkflowRuntimeError(
                "Incoming metadata must be the same for all anchors."
            )

        self.provider.io.info(f"Connection {input_connection.name} Initialized!")

        input_connection.max_packet_size = 100

    def on_record_packet(self, input_connection: InputConnectionBase) -> None:
        """Handle the record packet received through the input connection."""
        self.provider.io.info("Record packet received!")
        self.output_anchor.write(input_connection.read())

    def on_complete(self) -> None:
        """Finalize the plugin."""
        self.provider.io.info("Completed processing records.")


AyxPlugin = register_plugin(AyxSdkMultipleInputAnchors)
