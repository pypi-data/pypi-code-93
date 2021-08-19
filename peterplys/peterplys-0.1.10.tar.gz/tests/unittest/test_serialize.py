from typing import List
from dataclasses import dataclass

from energytt_platform.serialize import JsonSerializer, Serializable


@dataclass
class NestedTestSerializable(Serializable):
    friends: List[str]


@dataclass
class TestSerializable(Serializable):
    name: str
    age: int
    nested: NestedTestSerializable


class TestJsonSerializer:

    def test__should_serialize_and_deserialize_correctly(self):

        # -- Arrange ---------------------------------------------------------

        obj = TestSerializable(
            name='John',
            age=50,
            nested=NestedTestSerializable(
                friends=['Bill', 'Joe', 'Tedd'],
            )
        )

        uut = JsonSerializer()

        # -- Act -------------------------------------------------------------

        serialized = uut.serialize(obj)
        deserialized = uut.deserialize(serialized, TestSerializable)

        # -- Assert ----------------------------------------------------------

        assert deserialized == obj
