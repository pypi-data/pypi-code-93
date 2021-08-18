from tsdoc0.python.comment_sentence import CommentSentence
from tsdoc0.python.model import Model
from tsdoc0.python.utils import repr_parent
from tsdoc0.python.segment import Segment
from typing import Final
from typing import Iterable
from typing import Optional

import attr


# This converter wrapper-function is used because of a bug with the mypy-attrs plugin.
# https://github.com/python/mypy/issues/8389
def _tuple(iterable: Iterable[CommentSentence]) -> tuple[CommentSentence, ...]:
    return tuple(iterable)


@attr.s(auto_attribs=True, kw_only=True)
class CommentAbstract(Segment):
    parent: Optional[Model] = attr.ib(eq=False, repr=repr_parent)
    indentation: Final[str]  # type: ignore[misc]
    sentences: Final[tuple[CommentSentence, ...]] = attr.ib(converter=_tuple)

    @property
    def answer(self) -> str:
        return self.sentences[0].callout if len(self.sentences) else ""

    @property
    def code(self) -> str:
        return "\n".join(sentence.code for sentence in self.sentences)

    @property
    def callout(self) -> str:
        return "\n".join(sentence.callout for sentence in self.sentences)
