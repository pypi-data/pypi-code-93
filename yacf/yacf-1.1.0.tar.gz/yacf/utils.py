"""Collection of utiility functions for the YACF package.
"""

# standard lib
from typing import Any, Union


def _get_depth(d: Any, depth=1) -> int:
    """Determines the depth of the dictionary

    :param d: Dictionary to check
    :return: the depth of the dictionary
    """
    if not isinstance(d, dict):
        return depth
    return max([_get_depth(x, depth=depth + 1) for x in d.keys()])


def add_dot_notations(d: dict, seperator: str) -> dict:
    """Takes a dictionary as input and concatenates the different keys together
    to access each configuration parameter with a single key.

    :param conf: configuration where the dot notation should be added.
    :param seperator: Seperating character to use for the dot-notation.
    :return: Updated dictionary which includes the dot notations
    """

    # First update all inner dictionaries
    for k in list(d.keys()):
        if isinstance(d[k], dict):
            d[k] = add_dot_notations(d[k], seperator)

    # Then update keys with dot notation
    for k in list(d.keys()):
        if isinstance(d[k], dict):
            for l in list(d[k].keys()):
                d[f"{k}.{l}"] = d[k][l]

    return d


def deep_update(this: dict, other: dict) -> dict:
    """Recursively updates the values of a dictionary.
    Just as with the regular dict.update() implementation does the function
    preferably uses the values of the other dictionary.

    Raises a type error, if not both of the parameters are dictionaries.

    :param value: Dictionary to update
    :param other: Other dictionary to merge into the first one.
    :return: Updated dictionary
    """

    for k, v in other.items():
        if isinstance(v, dict):
            this[k] = deep_update(this.get(k, {}), v)
        else:
            this[k] = other[k]

    return this
