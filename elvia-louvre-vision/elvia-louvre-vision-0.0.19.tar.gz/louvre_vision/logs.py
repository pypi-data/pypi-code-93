import logging
from typing import Any, Optional

from .data_models import Request


class LogEntry(logging.Logger):
    """Standardised logging."""
    def error(self, msg: Optional[Any] = None, *args, **kwargs):
        """
        Log an error.

        :param str msg: Message to log.
        :param str user_message: Message to show to the user. Optional.
        :param Request endpoint_request: Request subclass instance to help track the HTTP request. Optional.
        """
        user_message: Optional[Any] = kwargs.pop('user_message', None)
        endpoint_request = kwargs.pop('endpoint_request', None)

        strings = []
        if user_message:
            strings.append(str(user_message))
        if msg and isinstance(msg, str):
            strings.append(f'Error details: {msg}')
        if endpoint_request and isinstance(endpoint_request, Request):
            strings.append(f'{str(endpoint_request)}')
        super().error('\n'.join(string for string in strings), stack_info=True)

    def info(self, msg: Optional[Any] = None, *args, **kwargs):
        """
        Log an info trace.
        
        :param str msg: Message to log.
        :param Request endpoint_request: Request subclass instance to help track the HTTP request. Optional.
        """
        endpoint_request = kwargs.pop('endpoint_request', None)

        strings = []
        if msg and isinstance(msg, str):
            strings.append(str(msg))
        if endpoint_request and isinstance(endpoint_request, Request):
            strings.append(f'{str(endpoint_request)}')
        super().info('\n'.join(string for string in strings))

    def debug(self, msg: Optional[Any] = None, *args, **kwargs):
        """
        Log a debug trace.
        
        :param str msg: Message to log.
        :param Request endpoint_request: Request subclass instance to help track the HTTP request. Optional.
        """
        endpoint_request = kwargs.pop('endpoint_request', None)

        strings = []
        if msg and isinstance(msg, str):
            strings.append(str(msg))
        if endpoint_request and isinstance(endpoint_request, Request):
            strings.append(f'{str(endpoint_request)}')
        super().debug('\n'.join(string for string in strings))

    def warning(self, msg: Optional[Any] = None, *args, **kwargs):
        """
        Log a warning.
        
        :param str msg: Message to log.
        :param Request endpoint_request: Request subclass instance to help track the HTTP request. Optional.
        """
        endpoint_request = kwargs.pop('endpoint_request', None)

        strings = []
        if msg and isinstance(msg, str):
            strings.append(str(msg))
        if endpoint_request and isinstance(endpoint_request, Request):
            strings.append(f'{str(endpoint_request)}')
        super().warning('\n'.join(string for string in strings))
