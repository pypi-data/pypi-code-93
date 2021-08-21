# Copyright (c) Qotto, 2021

from typing import Union

from eventy.serialization import RecordSerializer
from eventy.record import Record, Event, Request, Response


class AvroSerializer(RecordSerializer):

    def encode(self, record: Record) -> bytes:
        raise NotImplementedError

    def decode(self, encoded: bytes) -> Union[Event, Request, Response]:
        raise NotImplementedError
