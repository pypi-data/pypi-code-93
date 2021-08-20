# Copyright (c) Qotto, 2021

"""
Messaging errors
"""

__all__ = [
    'MessagingError',
    'ConsumerCreationError',
    'ConsumerPollError',
    'ConsumerCommitError',
    'ProducerProduceError',
    'ProducerCreationError',
    'ProducerTransactionError',
]


class MessagingError(BaseException):
    """
    Base Error class of all messaging API
    """


class ConsumerCreationError(MessagingError):
    """
    A consumer could not be initialized
    """


class ConsumerPollError(MessagingError):
    """
    A consumer could not poll messages
    """


class ConsumerCommitError(MessagingError):
    """
    A consumer could not commit messages
    """


class ProducerCreationError(MessagingError):
    """
    A producer could not be initialized
    """


class ProducerProduceError(MessagingError):
    """
    A producer could not produce a message
    """


class ProducerTransactionError(MessagingError):
    """
    A transactional producer or processor could not commit a transaction
    """
