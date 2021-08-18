import json
import logging
import typing
from typing import Optional, Text, Dict

from convo.core.brokers.broker import CoreEventBroker

if typing.TYPE_CHECKING:
    from convo.utils.endpoints import EndpointConfiguration

logger = logging.getLogger(__name__)


class FileEventBroker(CoreEventBroker):
    """Log events to a file in json format.

    There will be one event per line and each event is stored as json."""

    BY_DEFAULT_LOG_FILE_NAME = "convo_event.log"

    def __init__(self, path: Optional[Text] = None) -> None:
        self.path = path or self.BY_DEFAULT_LOG_FILE_NAME
        self.event_logger = self._event_loging()

    @classmethod
    def from_endpoint_configuration(
        cls, broker_config: Optional["EndpointConfiguration"]
    ) -> Optional["FileEventBroker"]:
        if broker_config is None:
            return None

        # noinspection PyArgumentList
        return cls(**broker_config.kwargs)

    def _event_loging(self) -> logging.Logger:
        """Instantiate the file logger."""

        log_file = self.path
        # noinspection PyTypeChecker
        query_log = logging.getLogger("event-logger")
        query_log.setLevel(logging.INFO)
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter("%(message)s"))
        query_log.propagate = False
        query_log.addHandler(handler)

        logger.info(f"Logging events to '{log_file}'.")

        return query_log

    def announce(self, event: Dict) -> None:
        """Write event to file."""

        self.event_logger.info(json.dumps(event))
        self.event_logger.handlers[0].flush()
