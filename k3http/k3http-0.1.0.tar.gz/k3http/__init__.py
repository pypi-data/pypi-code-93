"""
HTTP/1.1 client

Use this module, we can set timeout, if timeout raise a 'socket.timeout'.
"""


__version__ = "0.1.0"
__name__ = "k3http"

from .client import (
    HttpError,
    LineTooLongError,
    ChunkedSizeError,
    NotConnectedError,
    ResponseNotReadyError,
    HeadersError,
    BadStatusLineError,
    Client,

)

from .util import(
    headers_add_host,
    request_add_host,
)

__all__ = [
    'HttpError',
    'LineTooLongError',
    'ChunkedSizeError',
    'NotConnectedError',
    'ResponseNotReadyError',
    'HeadersError',
    'BadStatusLineError',
    'Client',

    'headers_add_host',
    'request_add_host',
]

