""" Core definitions of data types. """
from __future__ import annotations

import io
from abc import ABC
from typing import Any, Optional
from io import BytesIO

import cbor2 as cbor

from .exceptions import InvalidDataError


class DataType(ABC):
    """ Generic parent class for all data types implementations. """

    type_code: int
    """ Globally unique numeric identifier for the data type. """
    type_name: str
    """ Globally unique identifier for the data type."""

    def __init__(self, value) -> None:
        self._value = value
        self.validate()

    @property
    def value(self):
        """ Current value of the instance. """
        return self._value

    @value.setter
    def value(self, value) -> None:
        if isinstance(value, bytes):
            value = self.decode(value)
        self._value = value

    @classmethod
    def read(cls, stream: io.BytesIO) -> Optional[DataType]:
        """Read the value from a binary stream.

        Args:
            stream: Binary stream containing the serialised data.

        Returns:
            An initialised instance of the DataType.
        """
        return cls.from_bytes(stream.read())

    def write(self, stream: io.BytesIO) -> io.BytesIO:
        """Write the value into a binary stream.

        Args:
            stream: Binary stream to serialise the value into.
        """
        stream.write(self.to_bytes())
        return stream

    def to_bytes(self) -> bytes:
        """ Convert the value into the binary representation. """
        return cbor.dumps(self.value)

    @classmethod
    def from_bytes(cls, data: bytes) -> Optional[DataType]:
        """Convert a binary representation into the corresponding value.

        Args:
            data: Serialised binary representation of the value.

        Returns:
            An initialised instance of the DataType.
        """
        value = cls.decode(data)
        if value is None:
            return None
        return cls(value)

    def set_from_bytes(self, data: bytes) -> None:
        """ Convert bytes and set the corresponding value on the instance. """
        self.value = self.decode(data)

    @classmethod
    def decode(cls, data: bytes) -> Any:
        """Convert a binary representation into the corresponding value.

        Args:
            data: Serialised binary representation of the value.

        Returns:
            Deserialised value.
        """
        with BytesIO(data) as fp:
            try:
                value = cbor.load(fp)
            except cbor.CBORDecodeError as ex:
                raise InvalidDataError("Invalid CBOR data") from ex
            if len(fp.read(1)) > 0:
                raise InvalidDataError("Excess CBOR data")
        return value

    @property
    def serialised_value(self) -> dict:
        """Return the sequence of values ready to be serialised.

        It is assumed that the serialisation will use the
        `serialised-value` serialiser.
        """
        return {"data-type-name": self.type_name, "bytes": self.to_bytes()}

    def validate(self) -> None:
        """Check the current value for correctness.

        Raises:
            `InvalidDataError`: If the value is invalid. By default there is no validation.
        """

    def __repr__(self):
        return f"<{type(self).__name__} value={self.value}>"

    def __str__(self):
        return str(self.value)

    def __eq__(self, other) -> bool:
        try:
            return self.type_name == other.type_name and self.value == other.value
        except AttributeError:
            return False
