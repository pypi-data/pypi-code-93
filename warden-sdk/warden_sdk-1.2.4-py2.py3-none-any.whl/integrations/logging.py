"""Logging Integration that handles the standard logging module. 

This integration allows us to capture all logs that were created throughout an application. This method allows a user to create logs without having to learn a new methodology, thus minimizing the amount of overheaded needed.

Code reference:
- [sentry_sdk](https://github.com/getsentry/sentry-python/blob/master/sentry_sdk/integrations/logging.py)
"""
from __future__ import absolute_import

import logging
import datetime
from fnmatch import fnmatch

from warden_sdk.hub import Hub
from warden_sdk.debug import (
   event_from_exception,
   current_stacktrace,
   capture_internal_exceptions,
)
from warden_sdk.utils import (
   iteritems
)
from warden_sdk.integrations import Integration

from logging import LogRecord
from typing import (
   Optional,
   Any,
   Dict
)

DEFAULT_LEVEL = logging.INFO
DEFAULT_EVENT_LEVEL = logging.ERROR


class LoggingIntegration(Integration):
   """LoggingIntegration integrates with the standard logging module.
   """
   identifier = "logging"

   def __init__(self, level: Optional[int] = DEFAULT_LEVEL, event_level: Optional[int] = DEFAULT_EVENT_LEVEL) -> None:
      self._handler = None

      if event_level is not None:
         self._handler = EventHandler(level=event_level)

   def _handle_record(self, record: LogRecord) -> None:
      if self._handler is not None and record.levelno >= self._handler.level:
         self._handler.handle(record)


   @staticmethod
   def setup_once() -> None:
      old_callhandlers = logging.Logger.callHandlers 

      def warden_patched_callhandlers(self: Any, record: LogRecord) -> Any:
         try:
            return old_callhandlers(self, record)
         finally:
            # This check is done twice, once also here before we even get
            # the integration.  Otherwise we have a high chance of getting
            # into a recursion error when the integration is resolved
            # (this also is slower).
            # if record.name not in _IGNORED_LOGGERS:
            integration = Hub.current.get_integration(LoggingIntegration)
            if integration is not None:
               integration._handle_record(record)

      logging.Logger.callHandlers = warden_patched_callhandlers  # type: ignore


def _logging_to_event_level(levelname: str) -> str:
   return {"critical": "fatal"}.get(levelname.lower(), levelname.lower())


COMMON_RECORD_ATTRS = frozenset(
   (
      "args",
      "created",
      "exc_info",
      "exc_text",
      "filename",
      "funcName",
      "levelname",
      "levelno",
      "linenno",
      "lineno",
      "message",
      "module",
      "msecs",
      "msg",
      "name",
      "pathname",
      "process",
      "processName",
      "relativeCreated",
      "stack",
      "tags",
      "thread",
      "threadName",
      "stack_info",
   )
)


def _extra_from_record(record: LogRecord) -> Dict[str, None]:
   return {
      k: v
      for k, v in iteritems(vars(record))
      if k not in COMMON_RECORD_ATTRS
      and (not isinstance(k, str) or not k.startswith("_"))
   }


class EventHandler(logging.Handler, object):
   """A logging handler that emits Warden events for each log record
   
   Note that you do not have to use this class if the logging integration is enabled, which it is by default.
   """

   def emit(self, record: LogRecord) -> Any:
      with capture_internal_exceptions():
         self.format(record)
         return self._emit(record)

   def _emit(self, record: LogRecord) -> None:
      hub = Hub.current
      if hub.client is None:
         return

      client_options = hub.client.options

      # exc_info might be None or (None, None, None)

      if record.exc_info and record.exc_info[0] is not None:
         event, hint = event_from_exception(
             record.exc_info,
             client_options=client_options,
             mechanism={"type": "logging", "handled": True},
         )
      elif record.exc_info and record.exc_info[0] is None:
         event = {}
         hint = {}
         with capture_internal_exceptions():
            event["threads"] = {
                "values": [
                    {
                        "stacktrace": current_stacktrace(
                            client_options["with_locals"]
                        ),
                        "crashed": False,
                        "current": True,
                    }
                ]
            }
      else:
         event = {}
         hint = {}

      event = {}
      hint = {}

      hint["log_record"] = record

      event["level"] = _logging_to_event_level(record.levelname)
      event["logger"] = record.name
      event["logentry"] = {"message": str(
          record.msg), "params": record.args}
      event["extra"] = _extra_from_record(record)

      hub.capture_event(event, hint=hint)
