# Copyright (c) Qotto, 2021

"""
Kafka implementation of the :mod:`eventy.messaging.transactional` API
"""

import logging

from confluent_kafka import Producer as KProducer, KafkaError

from .kafka_base import KafkaConsumer
from .kafka_errors import KafkaProducerCreationError, KafkaProducerTransactionError, KafkaConsumerCreationError
from eventy.messaging import TransactionalProducer, TransactionalProcessor
from eventy.record import Record
from eventy.serialization import ContextRecordSerializer, RecordSerializer

logger = logging.getLogger(__name__)

__all__ = [
    'KafkaTransactionalProcessor',
    'KafkaTransactionalProducer',
]


class KafkaTransactionalProducer(TransactionalProducer):

    def __init__(
        self,
        producer_config: dict[str, str],
        context_serializer: ContextRecordSerializer,
    ) -> None:
        self._context_serializer = context_serializer
        self._current_transaction: list[tuple[str, Record]] = list()
        try:
            # TODO: check sensible config (e.g. transactional.id) AND/OR provide sensible defaults
            self._transactional_producer = KProducer(producer_config)
            self._transactional_producer.init_transactions()
        except Exception as e:
            raise KafkaProducerCreationError from e

    def add_to_transaction(self, destination: str, record: Record, *args, **kwargs) -> None:
        self._current_transaction.append((destination, record))

    def commit(self):
        try:
            self._start_transaction()
            self._send_transaction_records()
            self._end_transaction()
        except Exception as e:
            raise KafkaProducerTransactionError from e

    def _start_transaction(self):
        self._transactional_producer.begin_transaction()

    def _send_transaction_records(self):
        for topic, record in self._current_transaction:
            message = self._context_serializer.encode(topic, record)
            self._transactional_producer.produce(topic, message, key=record.partition_key)

    def _end_transaction(self):
        if self._current_transaction:
            self._transactional_producer.commit_transaction()
            self._current_transaction.clear()


class KafkaTransactionalProcessor(KafkaTransactionalProducer, KafkaConsumer, TransactionalProcessor):

    def __init__(
        self,
        consumer_config: dict[str, str],
        consumer_topics: list[str],
        consumer_serializer: RecordSerializer,
        producer_config: dict[str, str],
        context_serializer: ContextRecordSerializer,
    ) -> None:
        try:
            KafkaConsumer.__init__(
                self,
                consumer_config,
                consumer_topics,
                consumer_serializer,
            )
            KafkaTransactionalProducer.__init__(
                self,
                producer_config,
                context_serializer,
            )
        except (KafkaConsumerCreationError, KafkaProducerCreationError) as e:
            raise KafkaProducerCreationError from e

    def _send_transaction_offsets(self):
        self._transactional_producer.send_offsets_to_transaction(
            self._kafka_consumer.position(self._kafka_consumer.assignment()),
            self._kafka_consumer.consumer_group_metadata(),
        )

    def commit(self):
        try:
            self._start_transaction()
            self._send_transaction_records()
            self._send_transaction_offsets()
        except Exception as e:
            # TODO: Some should be handled?
            # start can fail because it was already started on restart
            raise KafkaProducerTransactionError("Transaction could not start") from e
        try:
            self._end_transaction()
        except KafkaError as e:
            self._transactional_producer.abort_transaction()
            self._transactional_producer.begin_transaction()
            raise KafkaProducerTransactionError("Transaction aborted") from e
