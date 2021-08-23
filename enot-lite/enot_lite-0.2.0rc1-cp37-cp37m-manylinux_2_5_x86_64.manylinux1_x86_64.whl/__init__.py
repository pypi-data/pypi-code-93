from pathlib import Path

try:
    # Importing torch after ORT ld_preload leads to crash.
    # To avoid crash we must try to load torch before.
    import torch
except ImportError:
    pass


def _get_version() -> str:
    with Path(__file__).parent.joinpath('VERSION').open('r') as version_file:
        version = version_file.read().strip()

    return version


__version__ = _get_version()
