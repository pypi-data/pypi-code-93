from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, TypeVar, Optional, Tuple

from .property import Property


class WithPropertiesTrait(ABC):
    T = TypeVar("T", bound="WithPropertiesTrait")

    @abstractmethod
    def with_property(self: T, key: str, value: str, timestamp: Optional[datetime] = None) -> T:
        """

        :param key:
        :param value:
        :param timestamp:
        :return: itself
        """
        pass

    @abstractmethod
    def with_extended_properties(self: T, properties: List[Property]) -> T:
        """

        :param properties:
        :return: itself
        """
        pass

    @abstractmethod
    def with_properties(self: T, properties: List[Tuple[str, str]]) -> T:
        """

        :param properties:
        :return: itself
        """
        pass


@dataclass
class WithProperties(WithPropertiesTrait):
    properties: Optional[List[Property]] = None

    T = TypeVar("T", bound="WithProperties")

    def with_property(self: T, key: str, value: str, timestamp: Optional[datetime] = None) -> T:
        if self.properties is None:
            self.properties = []
        if timestamp is None:
            timestamp = datetime.now()
        self.properties.append(Property(key, value, timestamp))
        return self

    def with_extended_properties(self: T, properties: List[Property]) -> T:
        if self.properties is None:
            self.properties = []
        self.properties.extend(properties)
        return self

    def with_properties(self: T, properties: List[Tuple[str, str]]) -> T:
        if self.properties is None:
            self.properties = []
        for (key, value) in properties:
            self.properties.append(Property(key, value))
        return self


class WithDelegatedProperties(WithPropertiesTrait, ABC):
    T = TypeVar("T", bound="WithDelegatedProperties")

    @abstractmethod
    def _get_delegate(self) -> WithPropertiesTrait:
        pass

    def with_property(self: T, key: str, value: str, timestamp: Optional[datetime] = None) -> T:
        self._get_delegate().with_property(key, value, timestamp)
        return self

    def with_properties(self: T, properties: List[Tuple[str, str]]) -> T:
        self._get_delegate().with_properties(properties)
        return self

    def with_extended_properties(self: T, properties: List[Property]) -> T:
        self._get_delegate().with_extended_properties(properties)
        return self
