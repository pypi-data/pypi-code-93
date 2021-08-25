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
"""Example multiple input connection anchor tool."""
from ayx_python_sdk.core import (
    InputConnectionBase,
    Plugin,
    ProviderBase,
    register_plugin,
)
from ayx_python_sdk.core.exceptions import WorkflowRuntimeError


class AyxSdkMultiInputMultiOutputAnchor(Plugin):
    """Concrete implementation of an AyxPlugin."""

    def __init__(self, provider: ProviderBase) -> None:
        """Construct a plugin."""
        self.provider = provider
        self.provider.io.info("Plugin initialized.")

        self.input_anchors = [
            self.provider.get_input_anchor("Input1"),
            self.provider.get_input_anchor("Input2"),
        ]
        self.output_anchors = [
            self.provider.get_output_anchor("Output1"),
            self.provider.get_output_anchor("Output2"),
        ]

    def on_input_connection_opened(self, input_connection: InputConnectionBase) -> None:
        """Initialize the Input Connections of this plugin."""
        for output_anchor in self.output_anchors:
            if not output_anchor.is_open:
                output_anchor.open(input_connection.metadata)

        incoming_names = [field.name for field in input_connection.metadata]
        incoming_types = [field.type for field in input_connection.metadata]

        for output_anchor in self.output_anchors:
            outgoing_names = [field.name for field in output_anchor.metadata]
            outgoing_types = [field.type for field in output_anchor.metadata]

            if incoming_names != outgoing_names or incoming_types != outgoing_types:
                raise WorkflowRuntimeError(
                    "Incoming metadata must be the same for all anchors."
                )

            self.provider.io.info(f"Connection {input_connection.name} Initialized!")

    def on_record_packet(self, input_connection: InputConnectionBase) -> None:
        """Handle the record packet received through the input connection."""
        self.provider.io.info("Record packet received!")
        for output_anchor in self.output_anchors:
            output_anchor.write(input_connection.read())

    def on_complete(self) -> None:
        """Create all records."""
        self.provider.io.info("Completed processing records.")


AyxPlugin = register_plugin(AyxSdkMultiInputMultiOutputAnchor)
