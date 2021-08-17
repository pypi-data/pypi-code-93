"""The official `myst` python package owned by Myst AI, Inc."""
from typing import Optional

from myst.auth.credentials import authenticate
from myst.client import Client
from myst.core.data.time_array import TimeArray
from myst.core.time.time import Time
from myst.core.time.time_delta import TimeDelta
from myst.version import get_package_version

__version__ = get_package_version()

# Lazily instantiate the global client so that we don't form a connection pool at import time.
_client: Optional[Client] = None


def get_client() -> Client:
    """Returns the global Myst client instance."""
    global _client

    if _client is None:
        _client = Client()

    return _client


from myst.resources.time_series import TimeSeries

__all__ = ["authenticate", "Client", "Time", "TimeArray", "TimeDelta", "TimeSeries", "get_client"]
