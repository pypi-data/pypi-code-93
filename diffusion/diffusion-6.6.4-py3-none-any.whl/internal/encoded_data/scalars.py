""" Basic encoded data types. """
from __future__ import annotations

import ctypes
import io

from .abstract import EncodingType
from .exceptions import DataReadError, DataValidationError, StreamExhausted


class Int64(EncodingType):
    """Encodes 64-bit integers.

    Used as the generic class for smaller integer types.
    """

    width = 64

    def __init__(self, value: int):
        super().__init__(value)

    @classmethod
    def read(cls, stream: io.BytesIO) -> Int64:
        """ Read the encoded value from a binary stream. """
        shift = 0
        value = 0
        while shift < cls.width:
            data = stream.read(1)
            if len(data):
                byte_int = data[0]
            else:
                raise StreamExhausted("Stream exhausted")
            value |= (byte_int & 0x7F) << shift
            if byte_int & 0x80 == 0:
                return cls._from_unsigned(value)
            shift += 7
        raise DataReadError(f"Malformed integer: {value}.")

    @classmethod
    def _from_unsigned(cls, value: int) -> Int64:
        """ Constructs the instance of the class from an unsigned integer value. """
        return cls(ctypes.c_int64(value).value)

    def to_bytes(self) -> bytes:
        """ Convert the value into its bytes representation. """
        b_value = b""
        value = self.value
        while True:
            if value & ~0x7F == 0:
                b_value += bytes((value & 0xFF,))
                break
            b_value += bytes(((value & 0x7F) | 0x80,))
            value = (value % (1 << self.width)) >> 7  # logical right shift
        return b_value

    def validate(self) -> None:
        """Validate the value.

        Raises:
            `DataValidationError' if a value is considered invalid.
        """
        signed_max_value = 1 << (self.width - 1)
        if not -signed_max_value <= self.value < signed_max_value:
            unsigned_max_value = 1 << self.width
            if not 0 <= self.value < unsigned_max_value:
                raise DataValidationError(
                    f"Value `{self.value}` outside of bounds. Max width: {self.width} bits."
                )


class Int32(Int64):
    """ Encodes 32-bit integers. """

    width = 32

    @classmethod
    def _from_unsigned(cls, value):
        return cls(ctypes.c_int(value).value)


class Byte(Int64):
    """ Encodes 8-bit integers. """

    width = 8

    @classmethod
    def _from_unsigned(cls, value):
        return cls(ctypes.c_byte(value).value)


class Bytes(EncodingType):
    """ Encodes bytes values. """

    def __init__(self, value: bytes):
        super().__init__(value)

    @classmethod
    def read(cls, stream: io.BytesIO) -> Bytes:
        """ Read the encoded value from a binary stream. """
        length = Int32.read(stream)
        return cls(stream.read(length.value))

    def to_bytes(self) -> bytes:
        """ Convert the value into its bytes representation. """
        return Int32(len(self.value)).to_bytes() + self.value

    def validate(self) -> None:
        """Validate the value.

        Raises:
            `DataValidationError` if the value is not a bytestring.
        """
        if not isinstance(self.value, bytes):
            raise DataValidationError(f"`{self.value}` is not bytes.")


class FixedBytes(Bytes):
    """ Encodes bytes values of fixed length. """

    def __init__(self, value: bytes, length: int):
        self.length = length
        if len(value) != length:
            raise ValueError(f"The value has to be {length} bytes long.")
        super().__init__(value)

    @classmethod
    def read(cls, stream: io.BytesIO, length: int = 24) -> Bytes:
        """ Read the encoded value from a binary stream. """
        return cls(stream.read(length), length=length)

    def to_bytes(self) -> bytes:
        """ Convert the value into its bytes representation. """
        return self.value


class String(EncodingType):
    """ Encodes string values. """

    def __init__(self, value: str):
        super().__init__(value)

    @classmethod
    def read(cls, stream: io.BytesIO) -> String:
        """ Read the encoded value from a binary stream. """
        b_value = Bytes.read(stream)
        return cls(b_value.value.decode())

    def to_bytes(self) -> bytes:
        """ Convert the value into its bytes representation. """
        return Bytes(self.value.encode()).to_bytes()

    def validate(self) -> None:
        """Validate the value.

        Raises:
            DataValidationError: If the value is not a string.
        """
        if not isinstance(self.value, str):
            raise DataValidationError(f"`{self.value}` is not a string.")
