from typing import Union

from compound_types.built_ins.iterables import BoolIterable, DictIterable, \
    FloatIterable, IntIterable, StrIterable

BoolOrBoolIterable = Union[bool, BoolIterable]
DictOrDictIterable = Union[dict, DictIterable]
FloatOrFloatIterable = Union[float, FloatIterable]
IntOrIntIterable = Union[int, IntIterable]
StrOrStrIterable = Union[str, StrIterable]
