from tsdoc0.python.segment import Segment
from typing import Final
from typing import Iterable

import attr


# This converter wrapper-function is used because of a bug with the mypy-attrs plugin.
# https://github.com/python/mypy/issues/8389
def _tuple(iterable: Iterable[Segment]) -> tuple[Segment, ...]:
    return tuple(iterable)


@attr.s(auto_attribs=True, kw_only=True)
class Model:
    segments: Final[tuple[Segment, ...]] = attr.ib(converter=_tuple)
