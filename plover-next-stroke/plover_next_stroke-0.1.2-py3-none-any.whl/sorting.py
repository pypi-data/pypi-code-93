from enum import Enum
from typing import Tuple, Union, Callable

from plover import system


STROKE_TYPE = str
OUTLINE_TYPE = Tuple[STROKE_TYPE]


class SortingType(Enum):
    FREQUENCY = 0
    FREQUENCY_NUM = 1
    FREQUENCY_ALPHA = 2
    STROKE_COUNT = 3
    ALPHABETICAL = 4


sorting_descriptions = [
    "Frequency",
    "Frequency (Prioritize Numbers)",
    "Frequency (Prioritize Non-numeric)",
    "Stroke Count",
    "Alphabetical"
]


def to_int(string: str, default: int) -> int:
    try:
        return int(string)
    except ValueError:
        return default


def num_score(outline: OUTLINE_TYPE) -> Tuple[int, ...]:
    return tuple(to_int(s, 999999) for s in outline)


def get_sorter(sorting_type: SortingType) -> Callable[Tuple[OUTLINE_TYPE, str], Union[tuple, str, int]]:
    if sorting_type == SortingType.FREQUENCY:
        if system.ORTHOGRAPHY_WORDS is not None:
            return lambda s: (len(s[0]), system.ORTHOGRAPHY_WORDS.get(s[1], 999999))
        else:
            return lambda s: len(s[0])

    elif sorting_type == SortingType.FREQUENCY_NUM:
        if system.ORTHOGRAPHY_WORDS is not None:
            return lambda s: (num_score(s[0]), system.ORTHOGRAPHY_WORDS.get(s[1], 999999))
        else:
            return lambda s: num_score(s[0])

    elif sorting_type == SortingType.FREQUENCY_ALPHA:
        if system.ORTHOGRAPHY_WORDS is not None:
            return lambda s: (not s[0][-1].isalpha(), len(s[0]), system.ORTHOGRAPHY_WORDS.get(s[1], 999999))
        else:
            return lambda s: (not s[0][-1].isalpha(), len(s[0]))

    elif sorting_type == SortingType.STROKE_COUNT:
        return lambda s: len(s[0])

    elif sorting_type == SortingType.ALPHABETICAL:
        return lambda s: s[1].lower()
