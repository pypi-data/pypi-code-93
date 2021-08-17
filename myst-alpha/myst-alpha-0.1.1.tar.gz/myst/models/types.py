from typing import Any, List, Mapping, Tuple, Union
from uuid import UUID

UUIDOrStr = Union[str, UUID]
IntOrStr = Union[int, str]
Shape = Tuple[int, ...]
CoordinateLabels = Tuple[Tuple[IntOrStr, ...], ...]
AxisLabels = Tuple[IntOrStr, ...]
Metadata = Mapping[str, Union[str, int, float, bool, None]]

# Note: This should be a recursive type alias but `mypy` doesn't support that, so use `List[Any]` instead to allow for
#   an arbitrary amount of nesting.
ItemOrSlice = Union[Tuple[Union[IntOrStr, List[Any]], ...], List[Any], IntOrStr]
