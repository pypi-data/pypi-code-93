# Copyright (c) Qotto, 2021

"""
Messaging base API (Consumer and Producer)
"""

import logging
from typing import Iterable

from eventy.record import Record

logger = logging.getLogger(__name__)

__all__ = [
    'Consumer',
    'Producer',
]


class Consumer:
    """
    Abstract base class for a record consumer

    Allows batch polling, and manual or automatic after processing commit
    """

    def poll_commit(self, nb: int = 1, timeout: float = 0, *args, **kwargs) -> Iterable[Record]:
        """
        Infinite generator methods, with auto commit

        Poll records as batches of `nb` records, and commit the batch after the last record has been yielded.
        Previously polled records can be committed as soon as we are waiting for the next one.

        If records need to be polled ahead of time (e.g. for parallelization) and not be committed until after
        they are processed, the `poll()` method should be used.

        In case of synchronous processing, this method guarantees that messages are committed only after processing
        and the number of messages polled and not committed is at most `nb`.

        :param nb: Batch size, default 1
        :param timeout: Timeout for the batch poll in seconds, default 0 for infinite timeout
        :return: Polled records iterable
        :raise ConsumerPollError: On polling failure
        :raise ConsumerCommitError: On commit failure
        """
        while True:
            n = 0
            for record in self.poll(nb, timeout, *args, **kwargs):
                yield record
                n += 1
            if n > 0:
                logger.debug(f'Consumer will commit {n} records')
                self.commit()

    def poll(self, nb: int = 1, timeout: float = 0, *args, **kwargs) -> Iterable[Record]:
        """
        Poll a batch of records, without committing

        :param nb: Batch size, default 1
        :param timeout: Timeout for the batch poll in seconds, default 0 for infinite timeout
        :return: Polled records iterable
        :raise ConsumerPollError:
        """
        raise NotImplementedError

    def commit(self, *arg, **kwargs) -> None:
        """
        Commit all previously polled records

        Synchronous method, all previously polled records are committed on return

        :raise ConsumerCommitError:
        """
        raise NotImplementedError


class Producer:
    """
    Abstract base class for a record producer

    Allows to produce records synchronously
    """

    def produce_now(self, destination: str, record: Record, *arg, **kwargs) -> None:
        """
        Produce immediately a single record

        Synchronous method, the record is sent on return.

        :param destination: Destination of the record (e.g. a kafka topic)
        :param record: The record to be produced

        :raise ProducerProduceError: The record could not be produced
        """
        raise NotImplementedError
