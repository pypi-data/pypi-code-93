# Copyright (c) Qotto, 2021

"""
Kafka messaging errors
"""

from eventy.messaging.messaging_errors import (
    MessagingError,
    ConsumerPollError,
    ProducerTransactionError,
    ConsumerCommitError,
    ProducerProduceError,
    ConsumerCreationError,
    ProducerCreationError,
)

__all__ = [
    'KafkaError',
    'KafkaConsumerCreationError',
    'KafkaConsumerPollError',
    'KafkaTopicDeletionError',
    'KafkaProducerProduceError',
    'KafkaProducerTransactionError',
    'KafkaConsumerCommitError',
    'KafkaProducerCreationError',
    'KafkaTopicCreationError',
]


class KafkaError(MessagingError):
    """
    Base for all Kafka related errors
    """


class KafkaConsumerCreationError(KafkaError, ConsumerCreationError):
    """
    A Kafka consumer could not be created
    """


class KafkaConsumerPollError(KafkaError, ConsumerPollError):
    """
    A Kafka consumer could not poll messages
    """


class KafkaConsumerCommitError(KafkaError, ConsumerCommitError):
    """
    A Kafka consumer could not commit offsets
    """


class KafkaProducerCreationError(KafkaError, ProducerCreationError):
    """
    A Kafka producer could not be created
    """


class KafkaProducerProduceError(KafkaError, ProducerProduceError):
    """
    A kafka producer could not produce a message
    """


class KafkaProducerTransactionError(KafkaError, ProducerTransactionError):
    """
    A kafka producer could not commit a transaction
    """


class KafkaTopicCreationError(KafkaError):
    """
    Topic could not be created
    """


class KafkaTopicDeletionError(KafkaError):
    """
    Topic could not be deleted
    """
