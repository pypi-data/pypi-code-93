from typing import (Sequence as _abc_Sequence,
                    Iterable as _abc_Iterable,
                    Sized as _abc_Sized,
                    Mapping as _abc_Mapping)

from ._typed import Typed


# Integer
class Integer(Typed):
    expected_type = int


# Float
class Float(Typed):
    expected_type = float


# String
class String(Typed):
    expected_type = str


# Sequence
class Sequence(Typed):
    expected_type = _abc_Sequence


# Iterable
class Iterable(Typed):
    expected_type = _abc_Iterable


# Sized
class Sized(Typed):
    expected_type = _abc_Sized


# Mapping
class Mapping(Typed):
    expected_type = _abc_Mapping
