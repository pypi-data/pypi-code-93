from datetime import datetime, tzinfo
from typing import Union

timezone_input = Union[str, tzinfo, None]
timezone_output = Union[tzinfo, None]
dict_or_none = Union[dict, None]
bool_or_none = Union[bool, None]
str_or_none = Union[str, None]
datetime_or_none = Union[datetime, None]
