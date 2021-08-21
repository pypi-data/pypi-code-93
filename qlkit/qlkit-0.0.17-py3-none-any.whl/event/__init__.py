#!/usr/bin/env python
# -*- coding:utf-8 -*-

import typing as t
from abc import ABC, abstractmethod

"""
eg:
class IEventsTransfer(EventsTransfer):
    transfers = {
        "pusher_game": {
            "data_type": "protobuf",
            "message": game_pb2.PusherCallbackData
        },
    }

    def __init__(self, queue_name: str):
        if queue_name not in self.transfers:
            raise TypeError("queue_name must in transfers mapping!")

        if self.transfers["queue_name"]["data_type"] not in ["dict", "protobuf"]:
            raise TypeError("data_type must be dict or protobuf!")

        self.data_type = self.transfers["queue_name"]["data_type"]
        super(IEventsTransfer, self).__init__(queue_name)

    def serializer(self, data: t.Any) -> bytes:
        if self.data_type == "dict":
            return json.dumps(data)
        else:
            return MessageToJson(data)

    def deserializer(self, data: bytes) -> t.Any:
        if self.data_type == "dict":
            return json.loads(data)
        else:
            return Parse(data, self.transfers[self.queue_name]["message"])
"""


class EventsTransfer(ABC):
    transfers = {}

    def __init__(self, queue_name: str):
        """
        :param data_type: dict or protobuf
        """
        self.queue_name = queue_name

    @abstractmethod
    def serializer(self, data: t.Any) -> bytes:
        pass

    @abstractmethod
    def deserializer(self, data: bytes) -> t.Any:
        pass
