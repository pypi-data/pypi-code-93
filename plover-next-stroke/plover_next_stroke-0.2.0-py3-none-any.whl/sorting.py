from enum import Enum
from typing import Tuple, Union, Callable, Any, List, Optional

from plover import system


STROKE_TYPE = str
OUTLINE_TYPE = Tuple[STROKE_TYPE]


class SortingType(Enum):
    FREQUENCY = 0
    FREQUENCY_NUM = 1
    FREQUENCY_ALPHA = 2
    STROKE_COUNT = 3
    ALPHABETICAL = 4
    SYSTEM_DEFINED = 5


sorting_descriptions = [
    "Frequency",
    "Frequency (Prioritize Numbers)",
    "Frequency (Prioritize Non-numeric)",
    "Stroke Count",
    "Alphabetical",
    "System Defined"
]


def to_int(string: str, default: int) -> int:
    try:
        return int(string)
    except ValueError:
        return default


def num_score(outline: OUTLINE_TYPE) -> Tuple[int, ...]:
    return tuple(to_int(s, 999999) for s in outline)


def get_sorter(sorting_type: SortingType) -> Callable[[Tuple[OUTLINE_TYPE, str]], Any]:
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


def sort_suggestions(
    suggestions: List[Tuple[OUTLINE_TYPE, str]], 
    sorting_type: SortingType,
    stroke_formatter: Optional[Callable[[STROKE_TYPE], STROKE_TYPE]] = None,
    translation_formatter: Optional[Callable[[str], str]] = None,
    system_sorter: Optional[Callable[[Tuple[OUTLINE_TYPE, str]], Any]] = None
) -> List[Tuple[OUTLINE_TYPE, str]]:
    result = []
    for outline, translation in suggestions:
        if stroke_formatter is not None:
            outline = tuple(stroke_formatter(s) for s in outline)
        if translation_formatter is not None:
            translation = translation_formatter(translation)
        
        result.append((outline, translation))
    
    if sorting_type == SortingType.SYSTEM_DEFINED:
        if system_sorter is not None:
            return sorted(result, key=system_sorter)
        
        sorting_type = SortingType.FREQUENCY
    
    return sorted(result, key=get_sorter(sorting_type))
