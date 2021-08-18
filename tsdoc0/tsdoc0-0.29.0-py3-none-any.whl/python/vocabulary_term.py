from pathlib import Path
from tsdoc0.python.segment import Segment
from tsdoc0.python.utils import repr_parent
from typing import Final
from typing import Optional
from typing import TYPE_CHECKING

# Conditional import used because there would be a circular dependency
# https://mypy.readthedocs.io/en/latest/common_issues.html#import-cycles
if TYPE_CHECKING:
    from tsdoc0.python.vocabulary import Vocabulary  # noqa: F401

import attr
import csv

with open(Path(__file__, "..", "vocabulary_terms.csv").resolve()) as csvfile:
    _DICTIONARY: Final[tuple[dict[str, str], ...]] = tuple(
        row for row in csv.DictReader(csvfile, strict=True)
    )

_NAMES: Final[dict[str, str]] = {
    row["text"]: row["name"] for row in _DICTIONARY if len(row["name"]) > 0
}

_DEFINITIONS: Final[dict[str, str]] = {
    row["text"]: row["definition"] for row in _DICTIONARY
}

_INSTRUCTIONS: Final[dict[str, str]] = {
    row["text"]: row["instruction"] for row in _DICTIONARY
}


@attr.s(auto_attribs=True, kw_only=True)
class VocabularyTerm(Segment):
    # Forward reference used because there would be a circular dependency
    # https://mypy.readthedocs.io/en/latest/kinds_of_types.html#class-name-forward-references
    parent: Optional["Vocabulary"] = attr.ib(eq=False, repr=repr_parent)
    text: Final[str]  # type: ignore[misc]

    @property
    def name(self) -> str:
        return _NAMES.get(self.text, self.text)

    @property
    def definition(self) -> str:
        return _DEFINITIONS[self.text]

    @property
    def instruction(self) -> str:
        return _INSTRUCTIONS[self.text]
