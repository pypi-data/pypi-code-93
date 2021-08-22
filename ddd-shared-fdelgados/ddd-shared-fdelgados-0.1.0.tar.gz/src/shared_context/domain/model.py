from __future__ import annotations

import abc
import re
import uuid

from typing import List

from .events import DomainEvent


class AggregateRoot(metaclass=abc.ABCMeta):
    _events = []

    def record_event(self, event: DomainEvent):
        self._events.append(event)

    def events(self):
        events = self._events.copy()
        self._events.clear()

        return events


class Uuid(metaclass=abc.ABCMeta):
    __ID_PATTERN = r"[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$"

    def __init__(self, value: str = None):
        if not value:
            value = str(uuid.uuid4())

        self.__ensure_is_valid_id(value)
        self.__value = value

    def __ensure_is_valid_id(self, value: str):
        regex = re.compile(self.__ID_PATTERN, re.IGNORECASE)
        if not regex.match(value):
            raise ValueError("Invalid {} value".format(type(self).__name__))

    @property
    def value(self) -> str:
        return self.__value

    def __eq__(self, other: Uuid) -> bool:
        return self.value == other.value

    def __str__(self) -> str:
        return self.value

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return "<{}: {}>".format(type(self).__name__, self.value)


class Repository(metaclass=abc.ABCMeta):
    def __init__(self, aggregate: AggregateRoot):
        self.__aggregate = aggregate

    @classmethod
    def __subclasshook__(cls, subclass):
        if subclass is not Repository:
            return NotImplementedError

        if not hasattr(subclass, "add") or not callable(subclass.add):
            return NotImplementedError

        if not hasattr(subclass, "find") or not callable(subclass.find):
            return NotImplementedError

        if not hasattr(subclass, "find_all") or not callable(subclass.find_all):
            return NotImplementedError

        if not hasattr(subclass, "save") or not callable(subclass.save):
            return NotImplementedError

        return True

    @abc.abstractmethod
    def add(self, aggregate: AggregateRoot) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, aggregate: AggregateRoot) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def find(self, **kwargs) -> AggregateRoot:
        raise NotImplementedError

    @abc.abstractmethod
    def find_all(self, **kwargs) -> List[AggregateRoot]:
        raise NotImplementedError
