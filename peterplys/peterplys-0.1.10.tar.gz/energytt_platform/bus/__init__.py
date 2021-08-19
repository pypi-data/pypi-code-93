from typing import List

from .registry import message_registry
from .kafka import KafkaMessageBroker
from .serialize import MessageSerializer
from .dispatcher import MessageDispatcher
from .broker import MessageBroker, Message


def get_default_broker(servers: List[str]) -> MessageBroker:
    """
    Creates and returns an instance of the default message broker.

    :param List[str] servers:
    :rtype: MessageBroker
    :return: An instance of the default message broker
    """
    return KafkaMessageBroker(
        servers=servers,
        serializer=MessageSerializer(),
    )
