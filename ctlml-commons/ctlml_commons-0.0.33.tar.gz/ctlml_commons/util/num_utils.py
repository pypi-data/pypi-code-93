import math
from copy import deepcopy
from typing import Any, Dict, List, SupportsFloat
from numbers import Number


def percentage_format_str() -> str:
    """Returns a percentage formatting string to use when converting a number to a readable string.

    Returns: percentage formatting string
    """
    return "{0:.4f}%"


def number_to_percentage_str(value: Number, percentage_format: str = percentage_format_str()) -> str:
    """Converts a number to a string.

    Args:
        value: input number
        percentage_format: formatting string

    Returns: string representation of input number
    """
    return percentage_format.format(value)


def readable_number_to_str(an_input: Number, decimal_points: int = 20) -> str:
    """Converts a number to a string with an optional number of decimal points.

    Args:
        an_input: input number
        decimal_points: decimal points to use

    Returns: string representation of input number
    """
    format_str: str = '{:.' + str(decimal_points) + "f}"
    return format_str.format(an_input)


def convert_floats(input_data: Dict[str, Any], keys: List[str], default_value=None) -> Dict[str, Any]:
    """Converts values to floats in a dict based on keys to use.

    Args:
        input_data: input dict
        keys: keys to values that need converted to floats
        default_value: default value if the key is missing

    Returns: converted dict with fields updated to be floats
    """
    if any(k in input_data for k in keys):
        data = deepcopy(input_data)

        for key in keys:
            if key in input_data:
                data[key] = float(data[key]) if data[key] is not None else default_value

        return data

    return input_data


def is_zero(an_input: SupportsFloat) -> bool:
    """ Determines if a float-like input is close to zero.

    Args:
        an_input: float-like input

    Returns: if input is close to zero
    """
    return math.isclose(an_input, 0.0)


def percent_change(num_start: Number, num_end: Number) -> float:
    """Determine percentage change between 2 numbers.

    Args:
        num_start: starting number
        num_end: ending number

    Returns: percentage change
    """
    return (float(num_end) - float(num_start)) / float(num_start) * 100


# TODO: remove
def readable_float_to_str(an_input: float, decimal_points: int = 20) -> str:
    format_str: str = '{:.' + str(decimal_points) + "f}"
    return format_str.format(an_input)


# TODO: remove
def float_to_percentage_str(value: float, percentage_format: str = percentage_format_str()) -> str:
    """Deprecated. Converts a number to a string.

    Args:
        value: input number
        percentage_format: formatting string

    Returns: string representation of input number
    """
    return percentage_format.format(value)
