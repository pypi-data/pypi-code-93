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
"""Example input tool."""
from ayx_python_sdk.core import (
    FieldType,
    InputConnectionBase,
    Metadata,
    Plugin,
    ProviderBase,
    RecordPacket,
    register_plugin,
)
from ayx_python_sdk.core.exceptions import WorkflowRuntimeError


class AyxSdkInput(Plugin):
    """Concrete implementation of an AyxPlugin."""

    def __init__(self, provider: ProviderBase) -> None:
        """Construct a plugin."""
        self.provider = provider
        self.config_value = 0.42
        self.output_anchor = self.provider.get_output_anchor("Output")

        self.output_metadata = Metadata()
        self.output_metadata.add_field("x", FieldType.float)
        self.output_metadata.add_field("y", FieldType.v_wstring, size=100)
        self.output_metadata.add_field("z", FieldType.float)

        self.output_anchor.open(self.output_metadata)

        if float(self.config_value) > 0.5:
            raise WorkflowRuntimeError("Values greater than 0.5 are not allowed.")

        self.provider.io.info("Plugin initialized.")

    def on_input_connection_opened(self, input_connection: InputConnectionBase) -> None:
        """Initialize the Input Connections of this plugin."""
        raise NotImplementedError("Input tools don't have input connections.")

    def on_record_packet(self, input_connection: InputConnectionBase) -> None:
        """Handle the record packet received through the input connection."""
        raise NotImplementedError("Input tools don't receive packets.")

    def on_complete(self) -> None:
        """Create all records."""
        import pandas as pd

        df = pd.DataFrame(
            {
                "x": [1, 2, 3],
                "y": ["hello", "world", "from ayx_python_sdk!"],
                "z": [self.config_value, self.config_value, self.config_value],
            }
        )

        packet = RecordPacket.from_dataframe(self.output_metadata, df)

        self.output_anchor.write(packet)
        self.provider.io.info("Completed processing records.")


AyxPlugin = register_plugin(AyxSdkInput)
