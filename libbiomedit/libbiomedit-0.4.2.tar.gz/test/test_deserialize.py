import unittest
from enum import Enum
from typing import Tuple, Dict, Optional, Any
from dataclasses import dataclass

from libbiomedit.lib import deserialize


class TestDeserialize(unittest.TestCase):
    def test_deserialize_dataclass(self):
        @dataclass
        class Y:
            x: int
            y: Tuple[bool, bool]

        @dataclass
        class X:
            a: int
            pack: Y

        data = {"a": 1, "pack": {"x": 1, "y": [True, False]}}
        x = deserialize.deserialize(X)(data)

        self.assertEqual(x, X(a=1, pack=Y(x=1, y=(True, False))))

        with self.assertRaises(ValueError):
            deserialize.deserialize(Y)({"x": 1, "y": [True]})

    def test_deserialize_dict(self):
        @dataclass
        class Z:
            a: int
            dct: Dict[int, str]

        data = {"a": 1, "dct": {1: "x", 2: "y"}}
        z = deserialize.deserialize(Z)(data)

        self.assertEqual(z, Z(a=1, dct=data["dct"]))

    def test_deserialize_optional(self):
        self.assertEqual(deserialize.deserialize(Optional[int])(None), None)
        self.assertEqual(deserialize.deserialize(Optional[int])(1), 1)
        self.assertEqual(deserialize.deserialize(Any)(1), 1)
        self.assertEqual(deserialize.deserialize(Any)("1"), "1")

    def test_deserialize_tuple(self):
        with self.assertRaises(ValueError):
            deserialize.deserialize(Tuple[bool, bool])([True])
        self.assertEqual(
            deserialize.deserialize(Tuple[bool, bool])([True, False]), (True, False)
        )
        self.assertEqual(
            deserialize.deserialize(Tuple[bool, ...])([True, False]), (True, False)
        )
        self.assertEqual(deserialize.deserialize(Tuple[bool, ...])([True]), (True,))

    def test_deserialize_enum(self):
        class Color(Enum):
            RED = "red"
            BLUE = "blue"

        class Number(Enum):
            ONE = 1
            TWO = 2

        self.assertEqual(deserialize.deserialize(Color)("red"), Color.RED)
        self.assertEqual(deserialize.deserialize(Number)(2), Number.TWO)


class TestSerialize(unittest.TestCase):
    def test_serialize_dataclass(self):
        @dataclass
        class Y:
            x: int
            y: Tuple[bool, bool]

        @dataclass
        class X:
            a: int
            pack: Y

        obj = X(a=1, pack=Y(x=1, y=(True, False)))
        expected = {"a": 1, "pack": {"x": 1, "y": (True, False)}}
        data = deserialize.serialize(X)(obj)

        self.assertEqual(data, expected)

    def test_serialize_dict(self):
        @dataclass
        class Z:
            a: int
            dct: Dict[int, str]

        expected = {"a": 1, "dct": {1: "x", 2: "y"}}
        obj = Z(a=1, dct=expected["dct"])
        data = deserialize.serialize(Z)(obj)

        self.assertEqual(data, expected)

    def test_serialize_optional(self):
        self.assertEqual(deserialize.serialize(Optional[int])(None), None)
        self.assertEqual(deserialize.serialize(Optional[int])(1), 1)
        self.assertEqual(deserialize.serialize(Any)(1), 1)
        self.assertEqual(deserialize.serialize(Any)("1"), "1")

    def test_serialize_tuple(self):
        with self.assertRaises(ValueError):
            deserialize.serialize(Tuple[bool, bool])([True])
        self.assertEqual(
            deserialize.serialize(Tuple[bool, bool])([True, False]), (True, False)
        )
        self.assertEqual(
            deserialize.serialize(Tuple[bool, ...])([True, False]), (True, False)
        )
        self.assertEqual(deserialize.serialize(Tuple[bool, ...])([True]), (True,))

    def test_deserialize_enum(self):
        class Color(Enum):
            RED = "red"
            BLUE = "blue"

        class Number(Enum):
            ONE = 1
            TWO = 2

        self.assertEqual(deserialize.serialize(Color)(Color.RED), "red")
        self.assertEqual(deserialize.serialize(Number)(Number.TWO), 2)
