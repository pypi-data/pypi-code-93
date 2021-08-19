""" Abstract definition for encoded data. """

from __future__ import annotations

import io
from abc import ABCMeta, abstractmethod
from typing import Any

from typing_extensions import Protocol, runtime_checkable, Final


@runtime_checkable
class EncodingProtocol(Protocol):
    """General protocol for encoded data.

    Must be implemented for all classes which can be used to serialise
    and deserialise the data over the wire, even if they don't extend
    `EncodingType` directly. In other words, it allows for duck-typing
    serialisation/deserialisation.
    """

    @classmethod
    def read(cls, stream: io.BytesIO) -> EncodingProtocol:
        """Read the encoded value from a binary stream.

        It converts the read value to the correct type and constructs a new
        instance of the encoding type.
        """

    def write(self, stream: io.BytesIO) -> io.BytesIO:
        """ Write the bytes representation of a value into a binary stream. """

    def to_bytes(self) -> bytes:
        """ Convert the value into its bytes representation. """


class EncodingTypeMeta(ABCMeta):
    """ Metaclass for `EncodingType`, implementing functionalities on its subclasses. """

    def __repr__(cls):
        return f"encoded_data.{cls.__name__}"


class EncodingType(metaclass=EncodingTypeMeta):
    """ Base class for low-level encoding types. """

    value: Final[Any]

    def __init__(self, value: Any):
        self.value = value
        self.validate()

    @classmethod
    @abstractmethod
    def read(cls, stream: io.BytesIO) -> EncodingType:
        """Read the encoded value from a binary stream.

        It converts the read value to the correct type and constructs a new
        instance of the encoding type.
        """

    @abstractmethod
    def to_bytes(self) -> bytes:
        """ Convert the value into its bytes representation. """

    def write(self, stream: io.BytesIO) -> io.BytesIO:
        """ Write the bytes representation of a value into a binary stream. """
        stream.write(self.to_bytes())
        return stream

    def validate(self) -> None:
        """Validate the value.

        Raises:
            DataValidationError: If a value is considered invalid.
                                 By default there is no validation.
        """

    def __repr__(self):
        return f"{type(self).__name__}({repr(self.value)})"
