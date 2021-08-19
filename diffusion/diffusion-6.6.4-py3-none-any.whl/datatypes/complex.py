""" Complex data type definitions. """
from __future__ import annotations

from typing import Optional, Union

from .abstract import DataType
from .exceptions import InvalidDataError

JsonTypes = Union[dict, list, str, int, float]


class JsonDataType(DataType):
    """ JSON data type implementation. """

    type_code = 15
    type_name = "json"
    valid_types = JsonTypes.__args__  # type: ignore

    def __init__(self, value: Optional[JsonTypes]) -> None:
        super().__init__(value)

    def validate(self) -> None:
        """Check the current value for correctness.

        Raises:
            `InvalidDataError`: If the value is invalid.
        """
        if not (self.value is None or isinstance(self.value, self.valid_types)):
            raise InvalidDataError(
                "The value must be either None, or one of the following types:"
                f" {', '.join(t.__name__ for t in self.valid_types)};"
                f" got {type(self.value).__name__} instead."
            )


# TODO: complete implementation (FB23725)
class RecordDataType(DataType):
    """ Diffusion record data type implementation. """

    type_code = 20
    type_name = "record_v2"


# TODO: complete implementation (FB23725)
class TimeSeriesDataType(DataType):
    """ Time series data type implementation. """

    type_code = 16
    type_name = "time_series"


# TODO: complete implementation (FB23725)
class RoutingDataType(DataType):
    """ Time series data type implementation. """

    type_code = 12
    type_name = "routing"


# TODO: complete implementation (FB23725)
class UnknownDataType(DataType):
    """ Time series data type implementation. """

    type_code = 21
    type_name = "unknown"
