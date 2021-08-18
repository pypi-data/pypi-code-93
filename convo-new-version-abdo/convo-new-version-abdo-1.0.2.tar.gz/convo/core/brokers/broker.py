import logging
from typing import Any, Dict, Text, Optional, Union

import convo.shared.utils.common
from convo.utils.endpoints import EndpointConfiguration

logger = logging.getLogger(__name__)


class CoreEventBroker:
    """Base class for any event broker implementation."""

    @staticmethod
    def generate(
        obj: Union["CoreEventBroker", EndpointConfiguration, None],
    ) -> Optional["CoreEventBroker"]:
        """Factory to create an event broker."""
        if isinstance(obj, CoreEventBroker):
            return obj

        return _genrate_from_endpoint_configuration(obj)

    @classmethod
    def from_endpoint_configuration(cls, broker_config: EndpointConfiguration) -> "CoreEventBroker":
        raise NotImplementedError(
            "Event broker must implement the `from_endpoint_config` method."
        )

    def publish(self, event: Dict[Text, Any]) -> None:
        """Publishes a json-formatted Convo Core event into an event queue."""
        raise NotImplementedError("Event broker must implement the `publish` method.")

    def is_ready(self) -> bool:
        """Determine whether or not the event broker is ready.

        Returns:
            `True` by default, but this may be overridden by subclasses.
        """
        return True

    def shut(self) -> None:
        """Close the connection to an event broker."""
        # default implementation does nothing
        pass


def _genrate_from_endpoint_configuration(
    endpoint_config: Optional[EndpointConfiguration],
) -> Optional["CoreEventBroker"]:
    """Instantiate an event broker based on its configuration."""

    if endpoint_config is None:
        broker = None
    elif endpoint_config.type is None or endpoint_config.type.lower() == "pika":
        from convo.core.brokers.pika import PikaEventBroker

        # default broker if no type is set
        broker = PikaEventBroker.from_endpoint_configuration(endpoint_config)
    elif endpoint_config.type.lower() == "sql":
        from convo.core.brokers.sql import EventBrokerSQL

        broker = EventBrokerSQL.from_endpoint_configuration(endpoint_config)
    elif endpoint_config.type.lower() == "file":
        from convo.core.brokers.file import FileEventBroker

        broker = FileEventBroker.from_endpoint_configuration(endpoint_config)
    elif endpoint_config.type.lower() == "kafka":
        from convo.core.brokers.kafka import EventBrokerKafka

        broker = EventBrokerKafka.from_endpoint_configuration(endpoint_config)
    else:
        broker = _load_from_module_name_in_endpoint_configuration(endpoint_config)

    if broker:
        logger.debug(f"Instantiated event broker to '{broker.__class__.__name__}'.")
    return broker


def _load_from_module_name_in_endpoint_configuration(
    broker_config: EndpointConfiguration,
) -> Optional["CoreEventBroker"]:
    """Instantiate an event broker based on its class name."""
    try:
        broker_event_class = convo.shared.utils.common.class_name_from_module_path(
            broker_config.type
        )
        return broker_event_class.from_endpoint_configuration(broker_config)
    except (AttributeError, ImportError) as e:
        logger.warning(
            f"The `EventBroker` type '{broker_config.type}' could not be found. "
            f"Not using any event broker. Error: {e}"
        )
        return None
