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
"""Record Field class definition."""
from enum import Enum
from typing import Any, Optional


class FieldType(Enum):
    """Field types. The text values match the Alteryx Engine field types."""

    blob = "blob"
    byte = "byte"
    int16 = "int16"
    int32 = "int32"
    int64 = "int64"
    float = "float"
    double = "double"
    date = "date"
    time = "time"
    datetime = "datetime"
    bool = "bool"
    string = "string"
    v_string = "v_string"
    v_wstring = "v_wstring"
    wstring = "wstring"
    fixeddecimal = "fixeddecimal"
    spatialobj = "spatialobj"


class Field:
    """A record field that contains metadata like field name."""

    def __init__(
        self,
        name: str,
        field_type: FieldType,
        size: int = 0,
        scale: int = 0,
        source: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """
        Instantiate a field.

        Parameters
        ----------
        name
            The name of the field.
        field_type
            The type of data that this field represents.
        size
            The size of the data.

            For strings, this is the maximum number of characters.
            For blobs, this is the maximum number of bytes.
        scale
            The scale of the data. This only applies to fixeddecimal type.
        source
            The source of the data.
        description
            A description about the data that lives in this field.
        """
        self.name = name
        self.type = field_type
        self.size = size
        self.scale = scale
        self.source = source or ""
        self.description = description or ""

    def __eq__(self, other: Any) -> bool:
        """
        Determine if 2 fields are equal.

        Parameters
        ----------
        other
            Any other object to compare against.

        Returns
        -------
        bool
            True if all properties of this field match the other field.
        """
        if not isinstance(other, Field):
            return NotImplemented
        return (
            self.name == other.name
            and self.type == other.type
            and self.size == other.size
            and self.scale == other.scale
            and self.source == other.source
            and self.description == other.description
        )

    def __repr__(self) -> str:
        """
        Get the string representation of the object.

        Returns
        -------
        str
            The string representation of the metadata.
        """
        return (
            f"Field(name={self.name}, field_type={self.type}, size={self.size}, "
            f'scale={self.scale}, source="{self.source}", description="{self.description}")'
        )
