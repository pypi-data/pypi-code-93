"""Module containing datetime-related utility functions."""

from typing import Any

import pandas as pd

from trading.datasets.utils import string_utils


__all__ = [
    # Function exports
    'get_iso8601',
    'get_milliseconds',
    'get_seconds',
    'get_datetime',
]


def get_iso8601(value, **kwargs) -> str:
    value_ms = get_milliseconds(value, **kwargs)
    value = get_datetime(value, **kwargs)

    value_iso8601 = value.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-6] + "{:03d}"
    value_iso8601 = value_iso8601.format(int(value_ms) % 1000) + 'Z'

    return value_iso8601


def get_milliseconds(value, **kwargs):
    if isinstance(value, int) and string_utils.digitlen(value) >= 12:
        return value

    return get_seconds(value, **kwargs) * 1000


def get_seconds(value, **kwargs):
    if isinstance(value, int) and string_utils.digitlen(value) >= 12:
        return value / 1000

    return get_datetime(value, **kwargs).timestamp()


def get_datetime(value: Any, **kwargs) -> Any:
    """Returns the UTC datetime equivalent of the input value.

    Arguments:
        value: The generic input. This can be an iterable or a string or
            an input. The different cases are already covered by Pandas'
            internal `to_datetime()` function.
        kwargs: Any keyword arguments that we want to pass to Pandas'
            internal `to_datetime()` function.

    Return:
        A datetime object or an iterable of datetime objects.
    """
    try:
        # Input is an iterable, only convert the first element
        len(value)
        checkee = value[0]
    except (IndexError, TypeError, ValueError):
        checkee = value

    try:
        checkee = int(checkee)
    except (TypeError, ValueError):
        # Safe to pass here because we really just
        # want to try if we can conver the variable
        # into a pure integer
        pass

    # Millisecond case
    if isinstance(checkee, int) and string_utils.digitlen(checkee) >= 12:
        return pd.to_datetime(value, unit='ms', utc=True, **kwargs)

    return pd.to_datetime(value, utc=True, **kwargs)
