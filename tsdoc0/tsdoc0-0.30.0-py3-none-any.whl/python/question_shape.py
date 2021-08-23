from __future__ import annotations

from textx.exceptions import TextXSemanticError
from tsdoc0.python.answer_shape import AnswerShape
from tsdoc0.python.error_type import ErrorType
from tsdoc0.python.model import Model
from tsdoc0.python.segment import Segment
from tsdoc0.python.solution_code import SolutionCode
from tsdoc0.python.solution_shape import SolutionShape
from tsdoc0.python.utils import repr_parent
from typing import cast
from typing import Final
from typing import Optional

import attr


@attr.s(auto_attribs=True, kw_only=True)
class QuestionShape(Segment):
    parent: Optional[Model] = attr.ib(eq=False, repr=repr_parent)
    indentation: Final[str]  # type: ignore[misc]
    question: Final[str]  # type: ignore[misc]
    answer: Optional[AnswerShape]

    @classmethod
    def process_optional_answer(cls, question_shape: QuestionShape) -> None:
        if question_shape.answer:
            return

        if question_shape.parent is None:
            return

        segments = question_shape.parent.segments
        index_next = segments.index(question_shape) + 1
        segments_next = segments[index_next:]

        for segment in segments_next:
            if type(segment) is SolutionShape:
                segment = cast(SolutionShape, segment)

                question_shape.answer = AnswerShape(
                    parent=question_shape,
                    indentation=question_shape.indentation,
                    text=segment.answer,
                )
                return

            if type(segment) is SolutionCode:
                break

        raise TextXSemanticError(
            "Found no answer for a Shape Question",
            line=question_shape.line,
            col=question_shape.col,
            filename=question_shape.filename,
            err_type=ErrorType.FOUND_NO_ANSWER,
        )
