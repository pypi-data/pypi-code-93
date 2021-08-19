""" Module for defining serialisers.

    The key component is the `SERIALISER_SPECS` mapping, which is based on
    the specification in `spec.clj`.
"""

from .base import Serialiser
from .spec import NULL_VALUE_KEY, SERIALISER_SPECS, SerialiserMap


def get_serialiser(name: str = NULL_VALUE_KEY) -> Serialiser:
    """ Retrieve a serialiser instance based on the spec name. """
    return Serialiser.by_name(name)
