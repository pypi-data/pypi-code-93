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


class CustomDimensionsFilter(logging.Filter):
    """
    Add application-wide properties to AzureLogHandler records.
    Inspired by https://bargsten.org/wissen/python-logging-azure-custom-dimensions.html
    Workaround such that we are able to add 'Custom Properties' for the logs in Azure log
    """
    def __init__(self, custom_dimensions=None):
        """Create object with either input values or empty."""
        self.custom_dimensions = custom_dimensions or {}

    def filter(self, record):
        """Add the default custom_dimensions into the current log record."""
        cdim = self.custom_dimensions.copy()
        cdim.update(getattr(record, 'custom_dimensions', {}))
        record.custom_dimensions = cdim

        return True
