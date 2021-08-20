"""Misc utility functions"""
from posixpath import join as posixjoin
from urllib.parse import quote


def update_kwargs_for_key(kwargs: dict, key: str, values: dict):
    """Updates the passed in dictionary for the given key (using the dictionary `update` method of merging).

    If no value exists for the key, the supplied values dict is assigned directly.

    :param kwargs: The kwargs dictionary to modify in-place.
    :param key: The key to set (e.g. kwargs[key]).
    :param values: The values to update (e.g. kwargs[key].update(values)).
    """
    if key in kwargs:
        kwargs[key].update(values)
    else:
        kwargs[key] = values


def join_url_path(*elements) -> str:
    """Joins elements in a URL path after quoting them."""
    return posixjoin(*[quote(e, safe="") for e in elements])
