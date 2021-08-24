# Copyright (c) Qotto, 2021

"""
Event record
"""

from .record import Record

__all__ = [
    'Event',
]


class Event(Record):
    """
    Event implementation of the Record abstract base class
    """

    @property
    def type(self):
        """
        Record type (EVENT)

        :return: "EVENT"
        """
        return 'EVENT'
