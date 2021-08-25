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
"""Example pass through tool."""
from ayx_python_sdk.core import (
    FieldType,
    InputConnectionBase,
    Plugin,
    ProviderBase,
    RecordPacket,
    register_plugin,
)


class AyxSdkFilterLikeTool(Plugin):
    """A sample Plugin that filters numeric data for odd and even values."""

    def __init__(self, provider: ProviderBase):
        """Construct the AyxRecordProcessor."""
        self.provider = provider
        self.odd_output_anchor = self.provider.get_output_anchor("Output1")
        self.even_output_anchor = self.provider.get_output_anchor("Output2")
        self.provider.io.info("FilterLike tool started.")

    def on_input_connection_opened(self, input_connection: InputConnectionBase) -> None:
        """Initialize the Input Connections of this plugin."""
        if input_connection.metadata is None:
            raise RuntimeError("Metadata must be set before setting containers.")
        value_fields = [
            field for field in input_connection.metadata if field.name == "Value"
        ]
        if not value_fields:
            raise RuntimeError(
                "Incoming data must contain a column with the name 'Value'"
            )
        numeric_field_types = [
            FieldType.int16,
            FieldType.int32,
            FieldType.int64,
        ]
        if value_fields[0].type not in numeric_field_types:
            raise RuntimeError("'Value' column must be of 'int' data type")
        for output_anchor in [self.odd_output_anchor, self.even_output_anchor]:
            if not output_anchor.is_open:
                output_anchor.open(input_connection.metadata)

    def on_record_packet(self, input_connection: InputConnectionBase) -> None:
        """Handle the record packet received through the input connection."""
        packet = input_connection.read()
        input_dataframe = packet.to_dataframe()
        grouped = input_dataframe.groupby("Value")
        odds = grouped.filter(lambda row: row["Value"] % 2 == 1)
        evens = grouped.filter(lambda row: row["Value"] % 2 == 0)
        odd_packet = RecordPacket(metadata=input_connection.metadata, df=odds)
        even_packet = RecordPacket(metadata=input_connection.metadata, df=evens)
        self.odd_output_anchor.write(odd_packet)
        self.even_output_anchor.write(even_packet)

    def on_complete(self) -> None:
        """Handle for when the plugin is complete."""
        self.provider.io.info("FilterLike tool done.")


AyxPlugin = register_plugin(AyxSdkFilterLikeTool)
