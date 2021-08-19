"""inspect utilities."""

import inspect
from types import FrameType
from typing import cast


def caller_name() -> str:
    """Return the calling function's name."""
    # Ref: https://stackoverflow.com/a/57712700/
    return cast(FrameType, cast(FrameType, inspect.currentframe()).f_back).f_code.co_name
