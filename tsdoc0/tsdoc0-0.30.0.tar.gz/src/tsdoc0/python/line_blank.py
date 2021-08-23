from tsdoc0.python.model import Model
from tsdoc0.python.segment import Segment
from tsdoc0.python.utils import repr_parent
from typing import Final
from typing import Optional

import attr


@attr.s(auto_attribs=True, kw_only=True)
class LineBlank(Segment):
    parent: Optional[Model] = attr.ib(eq=False, repr=repr_parent)
    indentation: Final[str]  # type: ignore[misc]

    @property
    def code(self) -> str:
        return ""

    @property
    def callout(self) -> str:
        return ""
