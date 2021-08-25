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

"""Example tool that adds a new column with values that are calculated using another column."""


from ayx_python_sdk.core import (
    FieldType,
    InputConnectionBase,
    Plugin,
    ProviderBase,
    RecordPacket,
    register_plugin,
)
from ayx_python_sdk.core import exceptions


class AyxSdkDoubler(Plugin):
    """A sample tool that adds a calculated field."""

    def __init__(self, provider: ProviderBase):
        """Initialize the plugin."""
        self.provider = provider
        self.tool_config = provider.tool_config
        self.output_anchor = self.provider.get_output_anchor("Output")

    def on_input_connection_opened(self, input_connection: InputConnectionBase) -> None:
        """Initialize an InputConnection."""
        # check for existence of 'Value' column in input connection
        value = [field for field in input_connection.metadata if field.name == "Value"]
        if not len(value):
            raise exceptions.WorkflowRuntimeError(
                "Incoming data must contain a column with the name 'Value'"
            )

        numeric_field_types = [
            FieldType.double,
            FieldType.float,
            FieldType.int16,
            FieldType.int32,
            FieldType.int64,
        ]
        if value[0].type not in numeric_field_types:
            raise exceptions.WorkflowRuntimeError(
                "'Value' column must be a numeric data type"
            )

        output_metadata = input_connection.metadata.clone()
        output_metadata.add_field(name="Doubled", field_type=FieldType.double)
        self.output_anchor.open(output_metadata)

    def on_record_packet(self, connection: InputConnectionBase) -> None:
        """Process a packet of one or more records."""
        packet = connection.read()

        input_dataframe = packet.to_dataframe()

        output_dataframe = input_dataframe.copy()
        output_dataframe["Doubled"] = 2.0 * input_dataframe["Value"]

        output_packet = RecordPacket.from_dataframe(
            self.output_anchor.metadata, output_dataframe
        )

        self.output_anchor.write(output_packet)

    def on_complete(self) -> None:
        """Finalize the plugin."""
        self.provider.io.info("Doubler tool done.")


AyxPlugin = register_plugin(AyxSdkDoubler)
