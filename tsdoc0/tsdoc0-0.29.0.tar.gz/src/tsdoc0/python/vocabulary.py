from tsdoc0.python.model import Model
from tsdoc0.python.segment import Segment
from tsdoc0.python.vocabulary_term import VocabularyTerm
from tsdoc0.python.utils import repr_parent
from typing import Final
from typing import Iterable
from typing import Optional

import attr


# This converter wrapper-function is used because of a bug with the mypy-attrs plugin.
# https://github.com/python/mypy/issues/8389
def _tuple(iterable: Iterable[VocabularyTerm]) -> tuple[VocabularyTerm, ...]:
    return tuple(iterable)


@attr.s(auto_attribs=True, kw_only=True)
class Vocabulary(Segment):
    parent: Optional[Model] = attr.ib(eq=False, repr=repr_parent)
    indentation: Final[str]  # type: ignore[misc]
    terms: Final[tuple[VocabularyTerm, ...]] = attr.ib(converter=_tuple)
