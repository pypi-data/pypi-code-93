"""Excepthook Integration overrides the the default excepthook. 

This integration allows us to capture all exceptions thrown by the system and log them if we miss any when setting up `logger` or even if we setup try/except and catch specific errors.

Code reference:
- [sentry_sdk](https://github.com/getsentry/sentry-python/blob/master/sentry_sdk/integrations/excepthook.py)
"""
import sys

from warden_sdk.hub import Hub
from warden_sdk.debug import capture_internal_exceptions, event_from_exception
from warden_sdk.integrations import Integration


class ExcepthookIntegration(Integration):
   """Excepthook overrides default sys.excepthook.
   """
   identifier = "excepthook"

   always_run: bool = True

   def __init__(self, always_run:bool=True) -> None:

      if not isinstance(always_run, bool):
         raise ValueError(
             "Invalid value for always_run: %s (must be type boolean)"
             % (always_run,)
         )
      self.always_run = always_run

   @staticmethod
   def setup_once() -> None:
      """Override default `sys.excepthook`.
      """
      sys.excepthook = _make_excepthook(sys.excepthook)


def _make_excepthook(old_excepthook: Exception) -> Exception:
   """Setup new, custom excepthook.

   Captures the exception in the current Hub and shows which mechanism was used to capture that error.

   Args:
      old_excepthook: An exception raised in the system.

   Returns:
      A new excepthook for `warden_sdk`.
   """
   def warden_sdk_excepthook(type_, value, traceback) -> None:
      hub = Hub.current
      integration = hub.get_integration(ExcepthookIntegration)

      if integration is not None and _should_send(integration.always_run):
         client = hub.client
         with capture_internal_exceptions():
            event, hint = event_from_exception(
               (type_, value, traceback),
               client_options=client.options,
               mechanism={"type": "excepthook", "handled": False},
            )
            hub.capture_event(event, hint=hint)

      return old_excepthook(type_, value, traceback)

   return warden_sdk_excepthook

def _should_send(always_run: bool = False) -> bool:
    if always_run:
        return True

    if hasattr(sys, "ps1"):
        # Disable the excepthook for interactive Python shells, otherwise
        # every typo gets sent to Sentry.
        return False

    return True