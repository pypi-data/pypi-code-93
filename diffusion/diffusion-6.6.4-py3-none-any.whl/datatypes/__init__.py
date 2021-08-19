""" Diffusion data types. """

from __future__ import annotations

import sys
from inspect import isclass
from typing import cast, Mapping, Optional, Type, Union

from . import complex, primitives
from .abstract import DataType
from .exceptions import (
    DataTypeError,
    IncompatibleDatatypeError,
    InvalidDataError,
    UnknownDataTypeError,
)

DataTypeArgument = Union[int, str, Type[DataType]]

# datatype aliases for convenience
BINARY = primitives.BinaryDataType
DOUBLE = primitives.DoubleDataType
INT64 = primitives.Int64DataType
STRING = primitives.StringDataType
JSON = complex.JsonDataType
RECORD_V2 = complex.RecordDataType
ROUTING = complex.RoutingDataType
TIME_SERIES = complex.TimeSeriesDataType
UNKNOWN = complex.UnknownDataType

_dt_module = sys.modules[__name__]  # this module

# index and cache the implemented data types by type codes
_indexed_data_types: Mapping[int, Type[DataType]] = {
    item.type_code: item
    for item in vars(_dt_module).values()
    if isclass(item) and issubclass(item, DataType) and item is not DataType
}


def get(data_type: Optional[DataTypeArgument]) -> Type[DataType]:
    """Helper function to retrieve a datatype based on its name or a `DataTypes` value.

    Args:
        data_type: Either a string that corresponds to the `type_name` attribute
                   of a `DataType` subclass, or an integer that corresponds to the
                   `type_code` of a `DataType` subclass. It also accepts an actual
                   `DataType` subclass, which is returned unchanged.

    Raises:
        `UnknownDataTypeError`: If the corresponding data type was not found.

    Examples:
        >>> get('string')
        <class 'diffusion.datatypes.simple.StringDataType'>
        >>> get(INT64)
        <class 'diffusion.datatypes.simple.Int64DataType'>
        >>> get(15)
        <class 'diffusion.datatypes.complex.JsonDataType'>
    """
    if isinstance(data_type, str):
        data_type = getattr(_dt_module, data_type.strip().upper(), None)
    if isinstance(data_type, int):
        data_type = _indexed_data_types.get(data_type)
    if isclass(data_type) and issubclass(data_type, DataType):  # type: ignore
        return cast(Type[DataType], data_type)
    raise UnknownDataTypeError(f"Unknown data type '{data_type}'.")
