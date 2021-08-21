# Copyright (c) Qotto, 2021

"""
Kafka implementation of the :mod:`eventy.messaging.base` API
"""

import logging
from typing import Iterable

from confluent_kafka import Consumer as KConsumer, Producer as KProducer, Message as KMessage

from .kafka_errors import (
    KafkaConsumerCreationError,
    KafkaConsumerCommitError,
    KafkaProducerProduceError,
    KafkaProducerCreationError, KafkaConsumerPollError,
)
from eventy.messaging.base import Consumer, Producer
from eventy.record import Record
from eventy.serialization import RecordSerializer, ContextRecordSerializer

logger = logging.getLogger(__name__)

__all__ = [
    'KafkaConsumer',
    'KafkaProducer',
]


class KafkaConsumer(Consumer):
    """
    Consumer implementation using confluent kafka python client

    See:
        https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#pythonclient-consumer
    """

    def __init__(
        self,
        consumer_config: dict[str, str],
        consumer_topics: list[str],
        consumer_serializer: RecordSerializer,
    ) -> None:
        try:
            self._serializer = consumer_serializer
            self._kafka_consumer = KConsumer(consumer_config)
            self._active = False
            self._kafka_consumer.subscribe(
                consumer_topics,
                on_assign=self._on_assign, on_revoke=self._on_revoke, on_lost=self._on_lost
            )
        except Exception as e:
            raise KafkaConsumerCreationError from e
        self._nb_polled = 0

    def _on_assign(self, consumer, partitions):
        logger.debug(f"Partitions assigned {partitions}")

    def _on_revoke(self, consumer, partitions):
        logger.debug(f"Partitions revoked {partitions}")

    def _on_lost(self, consumer, partitions):
        logger.debug(f"Partitions lost {partitions}")

    def poll(self, nb: int = 1, timeout: float = 0, *arg, **kwargs) -> Iterable[Record]:
        try:
            messages: list[KMessage] = self._kafka_consumer.consume(nb, timeout=timeout)
        except Exception as e:
            raise KafkaConsumerPollError from e
        for message in messages:
            if not message:
                logger.debug(f"No message")
                continue

            logger.debug(f"{message.topic()}:{message.partition()}:{message.offset()} Polled kafka message")

            if message.error():
                logger.error(
                    f"{message.topic()}:{message.partition()}:{message.offset()} Message has error: {message.error()}"
                )
                continue

            # PyCharm complains but Message.value() does not have the 'payload' arg, it is the returned value
            # see Confluent API doc: https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#confluent_kafka.Message.value
            # noinspection PyArgumentList
            if not message.value():
                logger.warning(f"{message.topic()}:{message.partition()}:{message.offset()} Message has no value")
                continue

            try:
                # noinspection PyArgumentList
                record = self._serializer.decode(message.value())
                yield record
            except Exception as e:
                logger.error(
                    f"{message.topic()}:{message.partition()}:{message.offset()} Message could not be deserialized",
                    e, )
                continue

    def commit(self):
        try:
            self._kafka_consumer.commit(asynchronous=False)
        except Exception as e:
            # TODO: some exceptions are OK (nothing to commit yet)
            raise KafkaConsumerCommitError from e


class KafkaProducer(Producer):
    def __init__(
        self,
        producer_config: dict[str, str],
        context_serializer: ContextRecordSerializer,
    ) -> None:
        self._context_serializer = context_serializer
        self._delivery_status = None
        self._delivery_error = None
        try:
            self._kafka_producer = KProducer(producer_config)
        except Exception as e:
            raise KafkaProducerCreationError from e

    def _on_delivery(self, err, msg):
        if err:
            self._delivery_status = False
            self._delivery_error = err
        else:
            self._delivery_status = True
            self._delivered_msg: KMessage = msg

    def produce_now(self, destination: str, record: Record, *args, **kwargs):
        """
        Produce and flush (blocking)
        """

        try:
            encoded = self._context_serializer.encode(destination, record)
        except Exception as e:
            raise KafkaProducerProduceError('serialization failed') from e

        try:
            self._kafka_producer.produce(destination, encoded, record.partition_key, on_delivery=self._on_delivery)
            # TODO: should we try to purge() and retry in case of BufferError?
            self._kafka_producer.flush()
        except Exception as e:
            raise KafkaProducerProduceError from e

        if self._delivery_status:
            logger.debug(
                f'Delivered kafka message '
                f'{self._delivered_msg.topic()}:{self._delivered_msg.partition()}:{self._delivered_msg.offset()}'
            )
        else:
            raise KafkaProducerProduceError(f'Record was not delivered because: {self._delivery_error}')
