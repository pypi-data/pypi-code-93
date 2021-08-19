""" Simple data type definitions. """
from typing import Optional

from .abstract import DataType
from .exceptions import InvalidDataError


class BinaryDataType(DataType):
    """ Data type that supports arbitrary binary data. """

    type_code = 14
    type_name = "binary"

    def __init__(self, value: Optional[bytes]) -> None:
        super().__init__(value)

    def to_bytes(self) -> bytes:
        """ Convert the value into the binary representation. """
        return self.value

    @classmethod
    def decode(cls, data: bytes) -> bytes:
        """Convert a binary representation into the corresponding value.

        Args:
            data: Serialised binary representation of the value.

        Returns:
            Deserialised value.
        """
        return data

    def validate(self) -> None:
        """Check the current value for correctness.

        Raises:
            `InvalidDataError`: If the value is invalid.
        """
        if not (self.value is None or isinstance(self.value, bytes)):
            raise InvalidDataError(f"Expected bytes but got {type(self.value).__name__}")

    def __str__(self):
        return self.value.decode()


class StringDataType(DataType):
    """String data type.

    The string value is serialized as CBOR-format binary.
    """

    type_code = 17
    type_name = "string"

    def __init__(self, value: Optional[str]):
        super().__init__(value)

    def validate(self) -> None:
        """Check the current value for correctness.

        Raises:
            `InvalidDataError`: If the value is invalid.
        """
        if not (self.value is None or isinstance(self.value, str)):
            raise InvalidDataError("Expected string but got {type(self.value).__name__}")

    @classmethod
    def decode(cls, data: bytes) -> Optional[str]:
        """Convert a binary representation into the corresponding value.

        Args:
            data: Serialised binary representation of the value.

        Returns:
            Deserialised value.
        """
        return super().decode(data)

    def __str__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)


class Int64DataType(DataType):
    """Data type that supports 64-bit, signed integer values.

    The integer value is serialized as CBOR-format binary. A serialized value
    can be read as JSON instance.
    """

    type_code = 18
    type_name = "int64"
    MAX_VALUE = 1 << 63
    MIN_VALUE = -MAX_VALUE + 1

    def __init__(self, value: Optional[int]):
        super().__init__(value)

    @classmethod
    def decode(cls, data: bytes) -> Optional[int]:
        """Convert a binary representation into the corresponding value.

        Args:
            data: Serialised binary representation of the value.

        Returns:
            Deserialised value.
        """
        return super().decode(data)

    def validate(self) -> None:
        """Check the current value for correctness.

        Raises:
            `InvalidDataError`: If the value is invalid.
        """
        message = ""
        if self.value is not None:
            if not isinstance(self.value, int):
                message = f"Expected an integer but got {type(self.value).__name__}"
            elif not self.MIN_VALUE <= self.value <= self.MAX_VALUE:
                message = "Integer value out of bounds."
        if message:
            raise InvalidDataError(message)


class DoubleDataType(DataType):
    """Data type that supports double-precision floating point numbers.

    (Eight-byte IEEE 754)

    The integer value is serialized as CBOR-format binary. A serialized value
    can be read as a JSON instance.
    """

    type_code = 19
    type_name = "double"

    def __init__(self, value: Optional[float]):
        super().__init__(value)

    @classmethod
    def decode(cls, data: bytes) -> Optional[float]:
        """Convert a binary representation into the corresponding value.

        Args:
            data: Serialised binary representation of the value.

        Returns:
            Deserialised value.
        """
        return super().decode(data)

    def validate(self) -> None:
        """Check the current value for correctness.

        Raises:
            `InvalidDataError`: If the value is invalid.
        """
        if not (self.value is None or isinstance(self.value, float)):
            raise InvalidDataError(f"Expected a float but got {type(self.value).__name__}")
