# Copyright (c) Qotto, 2021

"""
Record serialization interfaces
"""

from typing import Any, Dict

from eventy.record import Record

__all__ = [
    'RecordSerializer',
    'ContextRecordSerializer',
    'DestinationRecordSerializer',
]


class RecordSerializer:
    """
    Record serializer interface
    """

    def encode(self, record: Record) -> Any:
        """
        Encode a record

        Raises:
            SerializationError
        """
        raise NotImplementedError

    def decode(self, encoded: Any) -> Record:
        """
        Decode a record

        Raises:
            SerializationError
        """
        raise NotImplementedError


class ContextRecordSerializer:
    def encode(self, context: Any, record: Record) -> Any:
        raise NotImplementedError

    def decode(self, context: Any, encoded: Any) -> Record:
        raise NotImplementedError


class DestinationRecordSerializer(ContextRecordSerializer):
    def __init__(
        self,
        default_serializer: RecordSerializer,
        destination_serializers: Dict[str, RecordSerializer] = None,
    ) -> None:
        self._default_serializer = default_serializer
        if not destination_serializers:
            destination_serializers = {}
        self._destination_serializers = destination_serializers.copy()

    def _select_serializer(self, context) -> RecordSerializer:
        serializer = self._destination_serializers.get(context)
        if serializer:
            return serializer
        else:
            return self._default_serializer

    def encode(self, context: str, record: Record) -> Any:
        serializer = self._select_serializer(context)
        return serializer.encode(record)

    def decode(self, context: str, encoded: Any) -> Record:
        serializer = self._select_serializer(context)
        return serializer.decode(encoded)
