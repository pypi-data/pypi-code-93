from ._typed import Typed


from collections.abc import Sequence as _abc_Sequence


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
