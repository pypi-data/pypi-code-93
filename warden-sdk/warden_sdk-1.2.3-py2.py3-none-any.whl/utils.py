"""Utility functions used to simplify redundant work across the SDK.

Code reference:
- [sentry_sdk](https://github.com/getsentry/sentry-python/blob/master/sentry_sdk/utils.py)
"""
import json
import logging
import sys

from datetime import datetime

from warden_sdk.consts import (DEFAULT_OPTIONS)

epoch = datetime(1970, 1, 1)

# The logger is created here but initialized in the debug support module
logger = logging.getLogger("warden_sdk.errors")

text_type = str
string_types = (text_type,)
number_types = (int, float)


def iteritems(x):
   return x.items()


def json_dumps(data):
   """Serialize data into a compact JSON representation encoded as UTF-8."""
   return json.dumps(data, allow_nan=False,
                     separators=(",", ":")).encode("utf-8")


def get_options(options) -> dict:
   rv = dict(DEFAULT_OPTIONS)
   options = dict(options)

   for key, value in iteritems(options):
      if key not in rv:
         raise TypeError("Unknown option %r" % (key,))
      rv[key] = value

   return rv


def reraise(tp, value, tb=None):
   assert value is not None
   if value.__traceback__ is not tb:
      raise value.with_traceback(tb)
   raise value


def _get_contextvars():
   if sys.version_info >= (3, 7):
      # On Python 3.7 context vars are functional
      from contextvars import ContextVar

      return True, ContextVar
   else:
      raise ImportError


def format_timestamp(value):
   # type: (datetime) -> str
   return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


HAS_REAL_CONTEXTVARS, ContextVar = _get_contextvars()

disable_capture_event = ContextVar("disable_capture_event")


def to_timestamp(value: datetime) -> float:
   return (value - epoch).total_seconds()


def to_string(value: str) -> str:
   try:
      return text_type(value)
   except UnicodeDecodeError:
      return repr(value)[1:-1]
