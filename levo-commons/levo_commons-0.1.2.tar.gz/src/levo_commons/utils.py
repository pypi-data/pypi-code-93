"""Various utility functions to avoid boilerplate when performing common operations."""
import pathlib
import sys
import traceback
from contextlib import contextmanager
from typing import Generator, Union
from urllib.parse import ParseResult, urlparse

import grpc


@contextmanager
def syspath_prepend(path: Union[pathlib.Path, str]) -> Generator:
    """Temporarily prepend `path` to `sys.path` for the duration of the `with` block."""
    # NOTE. It is not thread-safe to use as is now.
    # In the future it might require an `RLock` to avoid concurrent access to `sys.path`.
    current = sys.path[:]
    # Use `insert` to put the value to the 0th position in `sys.path`. The given path will be the first one to check.
    sys.path.insert(0, str(path))
    try:
        yield
    finally:
        sys.path[:] = current


def get_grpc_channel(url: str) -> grpc.Channel:
    """Connect to a gRPC channel.

    For HTTPS it returns a secure channel and an insecure one for HTTP.
    """
    parsed = urlparse(url)
    address = get_grpc_address(parsed)
    if parsed.scheme == "https":
        return grpc.secure_channel(address, grpc.ssl_channel_credentials())
    return grpc.insecure_channel(address)


def get_grpc_address(parsed: ParseResult) -> str:
    if parsed.port is not None:
        port = parsed.port
    else:
        port = 443 if parsed.scheme == "https" else 80
    return f"{parsed.hostname}:{port}"


def format_exception(error: Exception, include_traceback: bool = False) -> str:
    """Format exception as text."""
    error_type = type(error)
    if include_traceback:
        lines = traceback.format_exception(error_type, error, error.__traceback__)
    else:
        lines = traceback.format_exception_only(error_type, error)
    return "".join(lines)
