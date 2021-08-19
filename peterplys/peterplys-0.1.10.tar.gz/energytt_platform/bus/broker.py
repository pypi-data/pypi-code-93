from abc import abstractmethod
from dataclasses import dataclass
from typing import List, Iterable, Callable, Any

from energytt_platform.serialize import Serializable


# TMessage = Serializable


@dataclass
class Message(Serializable):
    """
    TODO
    """
    pass


TMessageHandler = Callable[[Message], None]


class MessageBroker(object):
    """
    Abstract base-class for publishing and consuming messages
    on the message-bus.
    """

    @abstractmethod
    def publish(self, topic: str, msg: Any, block=False, timeout=10):
        """
        Publish a message to a topic on the bus.

        :param str topic: The topic to publish to
        :param Any msg: The message to publish
        :param bool block: Whether to block until publishing is complete
        :param int timeout: Timeout in seconds (if block=True)
        """
        raise NotImplementedError

    @abstractmethod
    def listen(self, topics: List[str]) -> Iterable[Message]:
        """
        Subscribe to one or more topics. Returns an iterable of messages.

        :param List[str] topics: The topics to subscribe to
        :rtype: Iterable[Any]
        :return: An iterable of messages
        """
        raise NotImplementedError

    def subscribe(self, topics: List[str], handler: TMessageHandler):
        """
        An alias for subscribe() except this function takes a callable
        which is invoked for each message.

        :param List[str] topics: The topics to subscribe to
        :param TMessageHandler handler: Message handler
        """
        for msg in self.listen(topics):
            handler(msg)
