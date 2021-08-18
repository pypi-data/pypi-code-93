from textwrap import fill
from tsdoc0.python.segment import Segment
from tsdoc0.python.utils import repr_parent
from typing import Final
from typing import TYPE_CHECKING
from typing import Union

# Conditional import used because there would be a circular dependency
# https://mypy.readthedocs.io/en/latest/common_issues.html#import-cycles
if TYPE_CHECKING:
    from tsdoc0.python.comment_abstract import CommentAbstract
    from tsdoc0.python.comment_concrete import CommentConcrete


import attr


@attr.s(auto_attribs=True, kw_only=True)
class CommentSentence(Segment):
    # Forward reference used because there would be a circular dependency
    # https://mypy.readthedocs.io/en/latest/kinds_of_types.html#class-name-forward-references
    parent: Union["CommentAbstract", "CommentConcrete", None] = attr.ib(
        eq=False, repr=repr_parent
    )
    indentation: Final[str]  # type: ignore[misc]
    text: Final[str]  # type: ignore[misc]

    @property
    def code(self) -> str:
        text_pruned = self.text.replace("`", "").removesuffix(".")
        return self._wrap_comment_or_ignore_string_literal(text_pruned)

    def _wrap_comment_or_ignore_string_literal(self, text: str) -> str:
        # Entire-line string literals are not wrapped because students' may want to
        # copy-and-paste them into their code.
        if text.startswith('"') and text.endswith('"'):
            return f"{self.indentation}# {text}"

        indent = f"{self.indentation}# "
        width = 55

        return fill(text, width, initial_indent=indent, subsequent_indent=indent)

    @property
    def callout(self) -> str:
        return self.text
