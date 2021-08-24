"""Module containing cache-related utility functions.

The cache (default to `~/.cache/trading-datasets/`) is used for
any datasets that are returned by the Trading Datasets Library.

The only variation from the default directory is if:

* The user specified another cache directory through the
  environment variable `TDS_CACHE_DIR`.
* The user is using a notebook-like environment. We want
  the user to be able to see the cache file directly that's
  why we will use a more "exposed" directory.

"""

import os
import pathlib


__all__ = [
    # Function exports
    'cache_path',
]


def _default_cache_dir(exposed: bool = False) -> pathlib.Path:
    """Returns the default cache directory.

    Arguments:
        exposed: Used to forcefully make the default cache dir
            easily seeable or "exposed" to the user.

    Return:
        The path to the default cache directory.
    """
    base_dir = 'trading-datasets'

    # Use environment variable if the user set something there
    if 'TDS_CACHE_DIR' in os.environ:
        path = os.environ['TDS_CACHE_DIR']

    else:
        if exposed:
            # Module is used in a notebook-like environment
            # so we want to show the cache directory to the user
            path = os.path.abspath('')
        else:
            # Module is running in a non-notebook environment
            # so we want to put it in a standard cache directory
            path = os.path.join('~', '.cache')

    # Always make sure that the last directory
    # is our base directory
    path = os.path.join(path, base_dir)

    return pathlib.Path(path).expanduser()


def cache_path() -> pathlib.Path:  # pragma: no cover
    """Returns the path to the Trading Datasets cache."""
    path = _default_cache_dir()
    path.mkdir(parents=True, exist_ok=True)

    return path
