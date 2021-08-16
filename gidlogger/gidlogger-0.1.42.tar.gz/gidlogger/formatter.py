"""
WiP.

Soon.
"""

# region [Imports]

import gc
import os
import re
import sys
import json
import queue
import math
from copy import deepcopy
import base64
import pickle
import random
import shelve
import dataclasses
import shutil
import asyncio
import logging
import sqlite3
import platform
import importlib
import subprocess
import unicodedata
import inspect

from time import sleep, process_time, process_time_ns, perf_counter, perf_counter_ns
from io import BytesIO, StringIO
from abc import ABC, ABCMeta, abstractmethod
from copy import copy, deepcopy
from enum import Enum, Flag, auto
from time import time, sleep
from pprint import pprint, pformat
from pathlib import Path
from string import Formatter, digits, printable, whitespace, punctuation, ascii_letters, ascii_lowercase, ascii_uppercase
from timeit import Timer
from typing import TYPE_CHECKING, Union, Callable, Iterable, Optional, Mapping, Any, IO, TextIO, BinaryIO
from zipfile import ZipFile, ZIP_LZMA
from datetime import datetime, timezone, timedelta
from tempfile import TemporaryDirectory
from textwrap import TextWrapper, fill, wrap, dedent, indent, shorten
from functools import wraps, partial, lru_cache, singledispatch, total_ordering, cached_property
from importlib import import_module, invalidate_caches
from contextlib import contextmanager, asynccontextmanager
from statistics import mean, mode, stdev, median, variance, pvariance, harmonic_mean, median_grouped
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from urllib.parse import urlparse
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from importlib.machinery import SourceFileLoader
from string import Formatter

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class AlignmentIndicator(Enum):
    NO_ALIGNMENT = ""
    CENTER = "^"
    LEFT_ALIGNMENT = "<"
    RIGHT_ALIGNMENT = ">"
    PADDING_AFTER_SIGN = "="

    @classmethod
    def _missing_(cls, value: object) -> Any:
        if isinstance(value, cls):
            return value
        if value is None:
            return cls.NO_ALIGNMENT
        alias_map = {'left': cls.LEFT_ALIGNMENT,
                     'right': cls.RIGHT_ALIGNMENT,
                     "center": cls.CENTER}

        if isinstance(value, str) and value.casefold() in alias_map:
            return alias_map.get(value.casefold())
        return super()._missing_(value)

    def __str__(self) -> str:
        return self.value


class FormatPart:

    def __init__(self, field_name: str, default_width: int = None, default_alignment: Union[str, AlignmentIndicator] = None, shorten_side: Union[str, None] = "right"):
        self.field_name = field_name
        self.default_width = default_width if default_width is not None else ""
        self.default_alignment = AlignmentIndicator(default_alignment)
        self.shorten_side = shorten_side
        self._width = None
        self._alignment = None

    @property
    def alignment(self) -> str:
        if self._alignment is None:
            return self.default_alignment
        return self._alignment

    @alignment.setter
    def alignment(self, data: str):
        self._alignment = AlignmentIndicator(data)

    @property
    def width(self) -> int:
        if self._width is None:
            return self.default_width
        return self._width

    @width.setter
    def width(self, data: int):
        if data is None:
            self._width = ""
        else:
            self._width = data

    @property
    def width_format_spec(self):
        if self.width == "":
            return ""
        return ":{self.alignment!s}{self.width!s}"

    @property
    def raw_format(self):

        raw = "{{" + self.field_name + self.width_format_spec + "}}"
        return raw

    def format_attribute(self, attr: float) -> str:
        if self.width == "" or not isinstance(attr, str) or self.shorten_side is None:
            return attr

        if len(attr) > self.width:
            if self.shorten_side == "right":
                return attr[:(self.width - 3)] + '...'
            if self.shorten_side == "left":
                return '...' + attr[-(self.width - 3):]
        return attr

    def __str__(self) -> str:

        return self.raw_format.format(self=self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(field_name={self.field_name!r})"


class TimeFormatPart(FormatPart):

    def __init__(self, default_width: int = None, default_alignment: Union[str, AlignmentIndicator] = None, shorten_side: Union[str, None] = None, default_milliseconds_digits: int = None):
        super().__init__("asctime", default_width=default_width, default_alignment=default_alignment, shorten_side=shorten_side)
        self.default_milliseconds_digits = default_milliseconds_digits
        self._milliseconds_digits = None

    @property
    def use_miliseconds(self):
        return self.milliseconds_digits not in {None, ""}

    @property
    def milliseconds_digits(self) -> str:
        if self._milliseconds_digits is None:
            return self.default_milliseconds_digits
        return self._milliseconds_digits

    @milliseconds_digits.setter
    def milliseconds_digits(self, data: int):
        self._milliseconds_digits = data if data is not None else ""

    @property
    def milliseconds_format(self):
        if self.use_miliseconds is False:
            return None
        return "{msecs" + f":0{self.milliseconds_digits}.0f" + '}'

    def format_attribute(self, attr: float) -> str:
        if self.use_miliseconds is False or isinstance(attr, str):
            return attr
        return self.milliseconds_format.format(msecs=attr)

    @property
    def width(self) -> int:
        if self._width is None:
            width = self.default_width
        else:
            width = self._width

        if self.use_miliseconds is False or width == "" or self.alignment in {AlignmentIndicator.NO_ALIGNMENT, AlignmentIndicator.LEFT_ALIGNMENT, AlignmentIndicator.RIGHT_ALIGNMENT}:
            return width
        else:
            return max(width // 2, 1)

    @width.setter
    def width(self, data: int):
        if data is None:
            self._width = ""
        else:
            self._width = data

    @property
    def width_format_spec(self):
        if self.width == "":
            return ("", "")
        if self.use_miliseconds is False:
            return (":{self.alignment!s}{self.width!s}", "")
        else:
            if self.alignment is AlignmentIndicator.CENTER:

                return (":" + AlignmentIndicator.RIGHT_ALIGNMENT.value + "{self.width!s}", ":" + AlignmentIndicator.LEFT_ALIGNMENT.value + "{self.width!s}")
            if self.alignment is AlignmentIndicator.RIGHT_ALIGNMENT:
                return (":" + AlignmentIndicator.RIGHT_ALIGNMENT.value + "{self.width!s}", "")
            if self.alignment is AlignmentIndicator.LEFT_ALIGNMENT or self.alignment is AlignmentIndicator.NO_ALIGNMENT:
                return ("", ":" + AlignmentIndicator.LEFT_ALIGNMENT.value + "{self.width!s}")

    @property
    def raw_format(self):
        if self.use_miliseconds is False:
            return "{{" + self.field_name + self.width_format_spec[0] + "}}"

        return "{{" + self.field_name + self.width_format_spec[0] + "}}.{{msecs" + self.width_format_spec[1] + "}}"

    def __str__(self) -> str:

        return self.raw_format.format(self=self)


class RelativeCreatedFormatPart(FormatPart):

    def __init__(self, default_width: int, default_alignment: Union[str, AlignmentIndicator], shorten_side: Union[str, None] = None, as_seconds: bool = True, digits_after_comma: int = None):
        super().__init__("relativeCreated", default_width=default_width, default_alignment=default_alignment, shorten_side=shorten_side)
        self.as_seconds = as_seconds
        self.digits_after_comma = digits_after_comma if digits_after_comma is not None else 3

    def format_attribute(self, attr: float) -> str:
        if self.as_seconds is False or isinstance(attr, str):
            return attr

        value = attr / 1000
        unit = "s" if self.as_seconds is True else 'ms'
        _format = "{value:" + "." + str(self.digits_after_comma) + "f}" + unit
        return _format.format(value=value)


class ToFileFormatter(logging.Formatter):
    """ Custom Formatter does these 2 things:
    1. Overrides 'funcName' with the value of 'func_name_override', if it exists.
    2. Overrides 'filename' with the value of 'file_name_override', if it exists.
    3. Shortens 'funcName' and 'filename' so to not cause issues with the formatting.
    """

    def __init__(self,
                 style: str = '%',
                 fmt: str = None,
                 attr_formatter: dict[str, FormatPart] = None,
                 datefmt: str = None,
                 error_formatter: Callable = None,
                 no_newline_on_error: bool = False) -> None:
        super().__init__(fmt=fmt, datefmt=datefmt, style=style, validate=True)
        self.attr_formatter = {} if attr_formatter is None else attr_formatter
        self.error_formatter = error_formatter
        self.no_newline_on_error = no_newline_on_error

    def format(self, record):
        record.name = record.name.removeprefix('main.')

        if hasattr(record, 'func_name_override'):
            record.funcName = record.func_name_override
        if hasattr(record, 'file_name_override'):
            record.filename = record.file_name_override
        for attr_name, attr_value in record.__dict__.items():
            if attr_name == 'msecs':
                formatter = self.attr_formatter.get('asctime', None)
            else:
                formatter = self.attr_formatter.get(attr_name, None)
            if formatter is not None:
                setattr(record, attr_name, formatter(attr_value))

        s = super().format(record)
        if record.exc_text:
            if self.no_newline_on_error is True:
                s = s.replace('\n', '')
        return s

    def formatException(self, ei) -> str:
        output = super().formatException(ei)
        if self.error_formatter is None:
            return output
        return self.error_formatter(output)


class FormatBuilder:
    field_parts = {'time': TimeFormatPart(default_width=None, default_alignment=None, default_milliseconds_digits=3),
                   'level_name': FormatPart(field_name="levelname", default_alignment=AlignmentIndicator.LEFT_ALIGNMENT, default_width=11),
                   'thread_name': FormatPart(field_name="threadName", default_alignment=AlignmentIndicator.CENTER, default_width=12),
                   'thread': FormatPart(field_name="thread", default_alignment=AlignmentIndicator.CENTER, default_width=5, shorten_side=None),
                   'line_number': FormatPart(field_name="lineno", default_alignment=AlignmentIndicator.CENTER, default_width=5),
                   'name': FormatPart(field_name="name", default_alignment=AlignmentIndicator.LEFT_ALIGNMENT, default_width=25),
                   'func_name': FormatPart(field_name='funcName', default_alignment=AlignmentIndicator.CENTER, default_width=25),
                   'message': FormatPart(field_name='message', default_alignment=None, default_width=None),
                   'relative_created': RelativeCreatedFormatPart(default_alignment=AlignmentIndicator.CENTER, default_width=10, as_seconds=True, digits_after_comma=3),
                   'path_name': FormatPart(field_name='pathname', default_alignment=AlignmentIndicator.LEFT_ALIGNMENT, default_width=50, shorten_side='left'),
                   'module': FormatPart(field_name="module", default_alignment=AlignmentIndicator.CENTER, default_width=15),
                   'level_number': FormatPart(field_name="levelno", default_alignment=AlignmentIndicator.CENTER, default_width=5, shorten_side=None),
                   'process': FormatPart(field_name='process', default_alignment=AlignmentIndicator.CENTER, default_width=5, shorten_side=None),
                   'process_name': FormatPart(field_name="processName", default_alignment=AlignmentIndicator.CENTER, default_width=15, shorten_side='right'), }

    default_date_format_map = {'file': "%Y-%m-%d_%H-%M-%S",
                               'stdout': "%H:%M:%S",
                               'general': "%Y-%m-%d %H:%M:%S"}

    default_field_seperator = "|"
    default_message_field_seperator = '||-->'

    def __init__(self, fields: Iterable[Union[str, dict]],
                 date_fmt: str = None,
                 field_seperator: str = None,
                 message_field_seperator: str = None,
                 formatter_cls: logging.Formatter = None) -> None:
        self._raw_field_data = list(fields)
        self.fields = self._handle_fields()
        self.date_fmt = self.default_date_format_map.get('general') if date_fmt is None else self.default_date_format_map.get(date_fmt, date_fmt)
        self.field_seperator = self.default_field_seperator if field_seperator is None else field_seperator
        self.message_field_seperator = self.default_message_field_seperator if message_field_seperator is None else message_field_seperator
        self.formatter_cls = ToFileFormatter if formatter_cls is None else formatter_cls

    def _handle_fields(self):
        fields = []
        if 'message' not in self._raw_field_data:
            self._raw_field_data.append("message")
        for item in self._raw_field_data:
            if isinstance(item, str):
                fields.append(deepcopy(self.field_parts.get(item.casefold())))
            elif isinstance(item, dict):
                if len(item) > 1:
                    # TODO: Custom error
                    raise RuntimeError('field dict should have the format {<field_name>: {<attr_name>: value}}, not ' + str(item))
                name = list(item)[0]
                field_item = deepcopy(self.field_parts.get(name.casefold()))
                values = list(item.values())[0]
                for attr_name, attr_value in values.items():
                    if hasattr(field_item, attr_name):
                        setattr(field_item, attr_name, attr_value)
                fields.append(field_item)

        return {field.field_name: field for field in fields}

    def get_format_string(self):
        std_fields = [value for key, value in self.fields.items() if key != 'message']
        std_field_string = f" {self.field_seperator} ".join(str(part) for part in std_fields)
        msg_field_string = f" {self.message_field_seperator} " + str(self.fields.get('message'))
        return std_field_string + msg_field_string

    def get_attr_formatter(self):
        return {field.field_name: field.format_attribute for field in self.fields.values()}

    def build(self, **kwargs):
        fmt_string = self.get_format_string()

        formatter = self.formatter_cls(style='{', fmt=fmt_string, datefmt=self.date_fmt, attr_formatter=self.get_attr_formatter(), **kwargs)
        return formatter


class PreMadeFormatterFactoryMeta(type):
    method_prefix = "_premade_"

    def __new__(cls, name, bases, attrs):

        klass = super().__new__(cls, name, bases, attrs)
        for meth_name, meth in attrs.items():
            if meth_name.startswith(cls.method_prefix):
                klass.available_formatter[meth_name.removeprefix(cls.method_prefix)] = meth_name

        return klass


class PreMadeFormatterFactory(metaclass=PreMadeFormatterFactoryMeta):
    builder = FormatBuilder
    available_formatter = {}

    @classmethod
    def get(cls, name, max_module_name_length: int = None, max_func_name_length: int = None, ** kwargs):
        formatter_meth_name = cls.available_formatter.get(name.casefold(), "_premade_general")
        return getattr(cls, formatter_meth_name)(max_module_name_length=max_module_name_length, max_func_name_length=max_func_name_length, ** kwargs)

    @classmethod
    def _premade_stdout(cls, max_module_name_length: int = None, max_func_name_length: int = None, **kwargs) -> logging.Formatter:
        func_name_field = "func_name" if max_func_name_length is None else {'func_name': {"width": max_func_name_length}}
        fields = [{"time": {"milliseconds_digits": None}},
                  "relative_created",
                  "level_name"]
        date_fmt = cls.builder.default_date_format_map.get('stdout')
        field_seperator = '|'
        message_field_seperator = '||-->'
        formatter_cls = ToFileFormatter
        builder = cls.builder(fields=fields, date_fmt=date_fmt, field_seperator=field_seperator, message_field_seperator=message_field_seperator, formatter_cls=formatter_cls)
        return builder.build(**kwargs)

    @classmethod
    def _premade_file(cls, max_module_name_length: int = None, max_func_name_length: int = None, **kwargs) -> logging.Formatter:
        name_field = "name" if max_module_name_length is None else {'name': {"width": max_module_name_length}}
        func_name_field = "func_name" if max_func_name_length is None else {'func_name': {"width": max_func_name_length}}
        fields = ["time",
                  "relative_created",
                  "level_name",
                  "path_name",
                  "line_number",
                  "thread_name",
                  name_field,
                  func_name_field,
                  ]
        date_fmt = cls.builder.default_date_format_map.get('file')
        field_seperator = '|'
        message_field_seperator = '||-->'
        formatter_cls = ToFileFormatter
        builder = cls.builder(fields=fields, date_fmt=date_fmt, field_seperator=field_seperator, message_field_seperator=message_field_seperator, formatter_cls=formatter_cls)
        return builder.build(**kwargs)

    @classmethod
    def _premade_general(cls, max_module_name_length: int = None, max_func_name_length: int = None, ** kwargs) -> logging.Formatter:
        name_field = "name" if max_module_name_length is None else {'name': {"width": max_module_name_length}}
        func_name_field = "func_name" if max_func_name_length is None else {'func_name': {"width": max_func_name_length}}
        fields = ["time",
                  "relative_created",
                  "level_name",
                  "thread_name",
                  name_field,
                  func_name_field,
                  "line_number", ]
        date_fmt = cls.builder.default_date_format_map.get('general')
        field_seperator = '|'
        message_field_seperator = '||-->'
        formatter_cls = ToFileFormatter
        builder = cls.builder(fields=fields, date_fmt=date_fmt, field_seperator=field_seperator, message_field_seperator=message_field_seperator, formatter_cls=formatter_cls)
        return builder.build(**kwargs)

        # region[Main_Exec]


if __name__ == '__main__':

    log = logging.getLogger("main")
    handler = logging.StreamHandler()
    handler.setFormatter(PreMadeFormatterFactory.get('stdout', max_module_name_length=18, max_func_name_length=27))
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)
    log.debug("test")
    log.info("test")
    log.warning("test")
    log.critical("test")
    log.error("test")
# endregion[Main_Exec]
