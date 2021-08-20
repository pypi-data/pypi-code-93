import logging
from typing import Any, Optional

from .data_models import EndpointRequest


class LogEntry(logging.Logger):
    """Standardised logging."""
    def error(self, msg: Optional[Any] = None, *args, **kwargs):

        user_message: Optional[Any] = kwargs.pop('user_message', None)
        endpoint_request = kwargs.pop('endpoint_request', None)

        strings = []
        if user_message:
            strings.append(str(user_message))
        if msg and isinstance(msg, str):
            strings.append(f'Error details: {msg}')
        if endpoint_request and isinstance(endpoint_request, EndpointRequest):
            strings.append(f'{str(endpoint_request)}')
        super().error('\n'.join(string for string in strings), stack_info=True)

    def info(self, msg: Optional[Any] = None, *args, **kwargs):

        endpoint_request = kwargs.pop('endpoint_request', None)

        strings = []
        if msg and isinstance(msg, str):
            strings.append(str(msg))
        if endpoint_request and isinstance(endpoint_request, EndpointRequest):
            strings.append(f'{str(endpoint_request)}')
        super().info('\n'.join(string for string in strings))

    def debug(self, msg: Optional[Any] = None, *args, **kwargs):

        endpoint_request = kwargs.pop('endpoint_request', None)

        strings = []
        if msg and isinstance(msg, str):
            strings.append(str(msg))
        if endpoint_request and isinstance(endpoint_request, EndpointRequest):
            strings.append(f'{str(endpoint_request)}')
        super().debug('\n'.join(string for string in strings))

    def warning(self, msg: Optional[Any] = None, *args, **kwargs):

        endpoint_request = kwargs.pop('endpoint_request', None)

        strings = []
        if msg and isinstance(msg, str):
            strings.append(str(msg))
        if endpoint_request and isinstance(endpoint_request, EndpointRequest):
            strings.append(f'{str(endpoint_request)}')
        super().warning('\n'.join(string for string in strings))
