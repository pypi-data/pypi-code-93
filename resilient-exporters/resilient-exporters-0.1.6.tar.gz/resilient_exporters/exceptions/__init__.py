# -*- coding: utf-8 -*-

"""
resilient_exporters.exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains the cutom exceptions used in resilient_exporters.
"""

__all__ = ["ResilientExporterException", "MissingModuleError",
           "MissingConfigError", "InvalidConfigError", "ExportError",
           "ConnectionError", "DataTypeError", "TimeoutError"]


class ResilientExporterException(Exception):
    """Something wrong occured when using exporters."""

    def __init__(self, exporter=None, message=None, *args, **kwargs):
        if exporter:
            self.type = type(exporter).__name__
            self.name = exporter.name
            self.content = f"Exception raised in {self.name} \
                            of type {self.type}"
            if message:
                self.content = f"{self.content} \n {message}"
            super(ResilientExporterException, self).__init__(self.content)
        else:
            super(ResilientExporterException, self).__init__(*args, **kwargs)


class MissingModuleError(ResilientExporterException, ModuleNotFoundError):
    """Module not found. Can be installed doing resilient-exporters[...]"""


class MissingConfigError(ResilientExporterException):
    """A piece of configuration is missing"""


class InvalidConfigError(ResilientExporterException):
    """A piece of configuration is wrong"""


class ExportError(ResilientExporterException):
    """An export job failed"""


class ConnectionError(ExportError):
    """Could not connect to target"""


class DataTypeError(ExportError, TypeError):
    """Provided is of the wrong type"""


class TimeoutError(ExportError):
    """An export attempt has timed out"""
