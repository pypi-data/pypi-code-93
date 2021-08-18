from __future__ import annotations

from textx.exceptions import TextXSemanticError
from tsdoc0.python.answer_abstract import AnswerAbstract
from tsdoc0.python.comment_abstract import CommentAbstract
from tsdoc0.python.error_type import ErrorType
from tsdoc0.python.model import Model
from tsdoc0.python.segment import Segment
from tsdoc0.python.solution_code import SolutionCode
from tsdoc0.python.utils import repr_parent
from typing import cast
from typing import Final
from typing import Optional

import attr


@attr.s(auto_attribs=True, kw_only=True)
class QuestionAbstract(Segment):
    parent: Optional[Model] = attr.ib(eq=False, repr=repr_parent)
    indentation: Final[str]  # type: ignore[misc]
    question: Final[str]  # type: ignore[misc]
    answer: Optional[AnswerAbstract]

    @classmethod
    def process_optional_answer(cls, question_abstract: QuestionAbstract) -> None:
        if question_abstract.answer:
            return

        if question_abstract.parent is None:
            return

        segments = question_abstract.parent.segments
        index_next = segments.index(question_abstract) + 1
        segments_next = segments[index_next:]

        for segment in segments_next:
            if type(segment) is CommentAbstract:
                segment = cast(CommentAbstract, segment)

                question_abstract.answer = AnswerAbstract(
                    parent=question_abstract,
                    indentation=question_abstract.indentation,
                    text=segment.answer,
                )
                return

            if type(segment) is SolutionCode:
                break

        raise TextXSemanticError(
            "Found no answer for an Abstract Question",
            line=question_abstract.line,
            col=question_abstract.col,
            filename=question_abstract.filename,
            err_type=ErrorType.FOUND_NO_ANSWER,
        )
