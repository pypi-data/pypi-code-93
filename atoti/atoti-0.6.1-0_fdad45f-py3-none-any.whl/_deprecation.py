import functools
import traceback
import warnings
from typing import Any, Callable, Collection, Optional


def deprecated(
    message: str, *, unless_called_from: Optional[Collection[str]] = None
) -> Callable:
    """Decorate deprecated function, class or method.

    Args:
        message: Explanation of the deprecation.
        unless_called_from: Avoid warning if one of the named functions is part of the last 3 calls of the traceback.
    """

    def decorator(function: Callable[[Any], Any]):
        @functools.wraps(function)
        def new_function(*args: Any, **kwargs: Any):
            warn = True
            if unless_called_from:
                stack = str(traceback.extract_stack(limit=3))
                warn = next(
                    (False for name in unless_called_from if f"in {name}" in stack),
                    warn,
                )
            if warn:
                # Using FutureWarning instead of DeprecationWarning because
                # DeprecationWarnings are hidden by default in IPython.
                # pandas does the same.
                # See:
                #  - https://docs.python.org/3/library/warnings.html#warning-categories
                #  - https://github.com/ipython/ipython/issues/8478
                warnings.warn(message, category=FutureWarning, stacklevel=2)
            return function(*args, **kwargs)

        return new_function

    return decorator
