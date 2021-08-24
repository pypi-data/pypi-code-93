from typing import Union

from compound_types.built_ins import DictList
from compound_types.built_ins.lists import BoolList, FloatList, IntList, StrList


BoolOrBoolList = Union[bool, BoolList]
DictOrDictList = Union[dict, DictList]
FloatOrFloatList = Union[float, FloatList]
IntOrIntList = Union[int, IntList]
StrOrStrList = Union[str, StrList]
