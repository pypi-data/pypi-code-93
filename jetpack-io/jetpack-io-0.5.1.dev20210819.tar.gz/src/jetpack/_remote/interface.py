import functools
from typing import Callable, NamedTuple

import jsonpickle
from jetpack import _remote
from jetpack._remote import codec
from jetpack.proto import remote_api_pb2

SERVER = _remote.Server()
CLIENT = _remote.Client()


def remote(fn: Callable) -> Callable:  # Decorator
    symbol = export(fn)
    stub = remote_function(symbol)
    return functools.wraps(fn)(stub)


def export(fn: Callable) -> str:
    return SERVER.export(fn)


def remote_function(symbol: str) -> Callable:
    return CLIENT.remote_function(symbol)
