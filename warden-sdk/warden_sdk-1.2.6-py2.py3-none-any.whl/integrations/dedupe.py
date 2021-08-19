from contextvars import ContextVar

from warden_sdk.hub import Hub
from warden_sdk.integrations import Integration
from warden_sdk.scope import add_global_event_processor

from typing import Optional

class DedupeIntegration(Integration):
    identifier = "dedupe"

    def __init__(self) -> None:
        self._last_seen = ContextVar("last-seen")

    @staticmethod
    def setup_once() -> None:
        @add_global_event_processor
        def processor(event, hint):
            if hint is None:
                return event

            integration = Hub.current.get_integration(DedupeIntegration)

            if integration is None:
                return event

            exc_info = hint.get("exc_info", None)
            if exc_info is None:
                return event

            exc = exc_info[1]
            if integration._last_seen.get(None) is exc:
                return None
            integration._last_seen.set(exc)
            return event
