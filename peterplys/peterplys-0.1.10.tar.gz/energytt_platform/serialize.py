import serpyco
from abc import abstractmethod
from functools import lru_cache
from dataclasses import dataclass
from typing import Dict, Type, TypeVar, Generic, Any, Optional


@dataclass
class Serializable:
    """
    Base class for dataclasses that can be serialized and deserialized.
    Subclasses must be defined as dataclasses.
    """

    @classmethod
    def create_from(cls, obj):
        """
        TODO Map properties of 'obj' to cls constructor.
        """
        return cls()

    def update(self, *objects):
        """
        TODO Copy properties from each object onto self
        """
        pass


# -- Interfaces --------------------------------------------------------------


TSerializable = TypeVar('TSerializable', bound=Serializable)
TSerialized = TypeVar('TSerialized')


class Serializer(Generic[TSerialized]):
    """
    An interface for serializing and deserializing dataclasses.
    """

    @abstractmethod
    def serialize(self, obj: TSerializable, cls: Optional[Type[TSerializable]] = None) -> TSerialized:
        """
        Serialize an object.
        """
        raise NotImplementedError

    @abstractmethod
    def deserialize(self, data: TSerialized, cls: Type[TSerializable]) -> TSerializable:
        """
        Deserialize an object.
        """
        raise NotImplementedError


# -- Serializers -------------------------------------------------------------


class SimpleSerializer(Serializer[Dict[str, Any]]):
    """
    Serialize and deserialize to and from simple Python types (dictionary).
    """
    def serialize(self, obj: TSerializable, cls: Optional[Type[TSerializable]] = None) -> Dict[str, Any]:
        """
        Serializes object to Python.
        """
        if cls is None:
            cls = obj.__class__
        return get_serpyco_serializer(cls).dump(obj)

    def deserialize(self, data: Dict[str, Any], cls: Type[TSerializable]) -> TSerializable:
        """
        Deserialize JSON data to instance of type "cls".
        """
        return get_serpyco_serializer(cls).load(data)


class JsonSerializer(Serializer[bytes]):
    """
    Serialize and deserialize to and from JSON (encoded bytes).
    """
    def serialize(self, obj: TSerializable, cls: Optional[Type[TSerializable]] = None) -> bytes:
        """
        Serializes object to JSON.
        """
        if cls is None:
            cls = obj.__class__
        return get_serpyco_serializer(cls).dump_json(obj).encode()

    def deserialize(self, data: bytes, cls: Type[TSerializable]) -> TSerializable:
        """
        Deserialize JSON data to instance of type "cls".
        """
        return get_serpyco_serializer(cls).load_json(data.decode('utf8'))


# -- Misc --------------------------------------------------------------------


@lru_cache
def get_serpyco_serializer(cls: Type[TSerializable]) -> serpyco.Serializer:
    """
    TODO
    """
    return serpyco.Serializer(cls, strict=True)


# -- Singletons --------------------------------------------------------------


json_serializer = JsonSerializer()
simple_serializer = SimpleSerializer()
