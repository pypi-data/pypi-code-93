from typing import Union, Sized, Iterable


BoolOrDict = Union[bool, dict]
BoolOrFloat = Union[bool, float]
BoolOrInt = Union[bool, int]
BoolOrStr = Union[bool, str]
DictOrFloat = Union[dict, float]
DictOrInt = Union[dict, int]
DictOrStr = Union[dict, str]
FloatOrInt = Union[float, int]
FloatOrStr = Union[float, str]
IntOrStr = Union[int, str]

Scalar = Union[int, float]
SizedOrIterable = Union[Sized, Iterable]
