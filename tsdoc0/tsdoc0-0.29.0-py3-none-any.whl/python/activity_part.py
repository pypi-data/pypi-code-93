from tsdoc0.python.segment import Segment
from tsdoc0.python.utils import repr_parent
from typing import Final
from typing import Optional
from typing import TYPE_CHECKING

# Conditional import used because there would be a circular dependency
# https://mypy.readthedocs.io/en/latest/common_issues.html#import-cycles
if TYPE_CHECKING:
    from tsdoc0.python.activity_header import ActivityHeader  # noqa: F401


import attr


@attr.s(auto_attribs=True, kw_only=True)
class ActivityPart(Segment):
    # Forward reference used because there would be a circular dependency
    # https://mypy.readthedocs.io/en/latest/kinds_of_types.html#class-name-forward-references
    parent: Optional["ActivityHeader"] = attr.ib(eq=False, repr=repr_parent)
    number: Final[str]  # type: ignore[misc]

    @property
    def code(self) -> str:
        return f"Part {self.number}: "
