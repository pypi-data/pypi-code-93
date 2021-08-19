""" Low-level encoding and decoding for transmitting data. """
from inspect import isclass

from .abstract import EncodingProtocol, EncodingType
from .exceptions import DataReadError
from .generics import GenericSet, StringSet
from .scalars import Byte, Bytes, Int32, Int64, String


def is_encoder(item) -> bool:
    """ Helper method to check if an object is an EncodingType class. """
    return isclass(item) and issubclass(item, EncodingProtocol)
