from tsdoc0.python.activity_part import ActivityPart
from tsdoc0.python.model import Model
from tsdoc0.python.segment import Segment
from tsdoc0.python.utils import repr_parent
from typing import Final
from typing import Optional

import attr


@attr.s(auto_attribs=True, kw_only=True)
class ActivityHeader(Segment):
    parent: Optional[Model] = attr.ib(eq=False, repr=repr_parent)
    subject_name: Final[str]  # type: ignore[misc]
    activity_type: Final[str]  # type: ignore[misc]
    topic_name: Final[str]  # type: ignore[misc]
    part: Optional[ActivityPart]
    program_name: Final[str]  # type: ignore[misc]

    @property
    def code(self) -> str:
        return (
            '"""\n'
            f"{self.subject_name}\n"
            f"{self.activity_type}: {self.topic_name}\n"
            f"{self.part.code if self.part else ''}{self.program_name}\n"
            '"""'
        )
