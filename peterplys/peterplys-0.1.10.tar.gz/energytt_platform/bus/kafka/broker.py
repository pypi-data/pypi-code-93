from typing import List, Any
from functools import cached_property
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError

from energytt_platform.bus.broker import MessageBroker
from energytt_platform.bus.exceptions import PublishError
from energytt_platform.bus.serialize import MessageSerializer


class KafkaMessageConsumer(object):
    """
    A consumer of Kafka messages.
    Iterates over messages in subscribed topics.
    """
    def __init__(
            self,
            topics: List[str],
            servers: List[str],
            serializer: MessageSerializer,
    ):
        """
        :param List[str] topics:
        :param List[str] servers:
        :param MessageSerializer serializer:
        """
        self.topics = topics
        self.servers = servers
        self.serializer = serializer

    @cached_property
    def consumer(self) -> KafkaConsumer:
        """
        TODO
        """
        return KafkaConsumer(
            *self.topics,
            bootstrap_servers=self.servers,
            value_deserializer=self.serializer.deserialize,
            auto_offset_reset='earliest',
            enable_auto_commit=False,
        )

    def __iter__(self):
        return (msg.value for msg in self.consumer)


class KafkaMessageBroker(MessageBroker):
    """
    Implementation of Kafka as message bus.
    """
    def __init__(self, servers: List[str], serializer: MessageSerializer):
        self.servers = servers
        self.serializer = serializer

    @cached_property
    def producer(self) -> KafkaProducer:
        """
        TODO
        """
        return KafkaProducer(
            bootstrap_servers=self.servers,
            value_serializer=self.serializer.serialize,
        )

    def publish(self, topic: str, msg: Any, block=True, timeout=10):
        """
        TODO
        """
        future = self.producer.send(
            topic=topic,
            value=msg,
        )

        if block:
            try:
                record_metadata = future.get(timeout=timeout)
            except KafkaError as e:
                # Decide what to do if produce request failed...
                raise PublishError(str(e))

    def listen(self, topics: List[str]) -> KafkaMessageConsumer:
        """
        TODO
        """
        return KafkaMessageConsumer(
            topics=topics,
            servers=self.servers,
            serializer=self.serializer,
        )
