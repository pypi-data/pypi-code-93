from __future__ import annotations

from typing import TYPE_CHECKING, Any, Collection, Mapping

from .._py4j_utils import as_java_object, to_java_object_array
from ..level import Level
from ..measure_description import MeasureDescription

if TYPE_CHECKING:
    from .._java_api import JavaApi
    from ..cube import Cube


def get_measure_name(
    *, java_api: JavaApi, measure: MeasureDescription, cube: Cube
) -> str:
    """Get the name of the measure from either a measure or its name."""
    return measure._distil(java_api=java_api, cube=cube)


def convert_level_in_description(levels: Collection[Level]) -> Collection[str]:
    """Get descriptions of the passed levels."""
    if any(not isinstance(level, Level) for level in levels):
        raise TypeError("All levels should be of type Level")
    return [level._java_description for level in levels]


def convert_measure_args(
    *, java_api: JavaApi, cube: Cube, args: Collection[Any]
) -> Collection[Any]:
    """Convert a collection of arguments used for creating a measure in Java.

    The ``Measure`` arguments are replaced by their name, and other arguments are
    translated into Java-equivalent objects when necessary.
    """
    return [_convert_measure_arg(java_api=java_api, cube=cube, arg=a) for a in args]


def _convert_measure_arg(*, java_api: JavaApi, cube: Cube, arg: Any) -> Any:
    # Replace measures with their name.
    if isinstance(arg, MeasureDescription):
        return get_measure_name(java_api=java_api, measure=arg, cube=cube)

    # Recursively convert nested args.
    if isinstance(arg, tuple):
        return to_java_object_array(
            convert_measure_args(java_api=java_api, cube=cube, args=arg),
            gateway=java_api.gateway,
        )
    if isinstance(arg, list):
        return convert_measure_args(java_api=java_api, cube=cube, args=arg)
    if isinstance(arg, Mapping):
        return {
            _convert_measure_arg(
                java_api=java_api, cube=cube, arg=key
            ): _convert_measure_arg(java_api=java_api, cube=cube, arg=value)
            for key, value in arg.items()
        }

    # Nothing smarter to do. Transform the argument to a java array.
    return as_java_object(arg, gateway=java_api.gateway)
