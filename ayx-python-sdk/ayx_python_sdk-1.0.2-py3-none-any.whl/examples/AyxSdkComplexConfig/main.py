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
"""Example passthrough tool with complex configuration."""
from datetime import date, datetime, time
from typing import List, Optional

from ayx_python_sdk.core import (
    InputConnectionBase,
    Plugin,
    ProviderBase,
    register_plugin,
)
from ayx_python_sdk.core.exceptions import WorkflowRuntimeError

from pydantic import BaseModel, validator


class AyxSdkComplexConfig(Plugin):
    """Concrete implementation of an AyxPlugin."""

    def __init__(self, provider: ProviderBase) -> None:
        """Construct a plugin."""
        # By defining the pydantic model definition inside the __init__ method,
        # we gain access to the methods/properties available on self, including
        # the provider. This is useful for developing custom, localized error messaging
        # for Designer when validation fails.
        class ConfigXml(BaseModel):
            """The pydantic XML class definition."""

            TextBox: str
            Number: int
            Date: date
            Time: time
            DateTime: datetime
            CheckBox1: bool
            CheckBox2: bool
            CheckBox3: bool
            Progress: float
            ListBoxStringSelector: Optional[List[str]]

            @validator("TextBox", pre=True)
            def textbox_validate_exists(cls, v):  # noqa: N805
                """Validate and cast the list box string selector value."""
                # Designer specific error messaging can be configured when validation fails.
                if v is None:
                    raise WorkflowRuntimeError("Text in Text Box must be specified.")

                return v

            @validator("ListBoxStringSelector", pre=True)
            def listbox_string_selector_validation_and_split(cls, v):  # noqa: N805
                """Validate and cast the list box string selector value."""
                # Validators can be used like this to perform validation and data mutation
                # prior to object construction.
                if v is None:
                    return []

                assert isinstance(v, str)
                return v.strip().split(",")

        self.provider = provider
        self.output_anchor = self.provider.get_output_anchor("Output")
        self.config = ConfigXml(**self.provider.tool_config)
        self.provider.io.info("Plugin initialized.")
        self.provider.io.info(f"TextBox says '{self.config.TextBox}'.")
        self.provider.io.info(f"The selected number is {self.config.Number}.")
        self.provider.io.info(f"The selected date is {self.config.Date}.")
        self.provider.io.info(f"The selected time is {self.config.Time}.")
        self.provider.io.info(f"The selected date time is {self.config.DateTime}.")
        self.provider.io.info(f"Checkbox 1 is {self.config.CheckBox1}.")
        self.provider.io.info(f"Checkbox 2 is  {self.config.CheckBox2}.")
        self.provider.io.info(f"Checkbox 3 is {self.config.CheckBox3}")
        self.provider.io.info(f"Progress is {self.config.Progress}.")
        self.provider.io.info(
            f"Selected values are: {self.config.ListBoxStringSelector}"
        )

    def on_input_connection_opened(self, input_connection: InputConnectionBase) -> None:
        """Initialize the Input Connections of this plugin."""
        self.output_anchor.open(input_connection.metadata)

    def on_record_packet(self, input_connection: InputConnectionBase) -> None:
        """Handle the record packet received through the input connection."""
        self.output_anchor.write(input_connection.read())

    def on_complete(self) -> None:
        """Create all records."""
        # Increment progress
        if self.config.Progress < 100:
            self.config.Progress += 10

        self.provider.environment.update_tool_config(self.config.dict())

        self.provider.io.info("Completed processing records.")


AyxPlugin = register_plugin(AyxSdkComplexConfig)
