# Copyright (c) Qotto, 2021

"""
Record serialization package

Define the interfaces for record serialization.
"""

from .record_serializer import RecordSerializer, DestinationRecordSerializer, ContextRecordSerializer
from .serialization_errors import SerializationError, UnknownRecordTypeError

__all__ = [
    'RecordSerializer',
    'ContextRecordSerializer',
    'DestinationRecordSerializer',
    'UnknownRecordTypeError',
    'SerializationError',
]
