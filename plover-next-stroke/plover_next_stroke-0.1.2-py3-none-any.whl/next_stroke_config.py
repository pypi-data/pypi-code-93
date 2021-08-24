from dataclasses import dataclass, replace

from plover_next_stroke.sorting import SortingType

@dataclass
class NextStrokeConfig:
    row_height: int = 30
    page_len: int = 10
    sorting_type: SortingType = SortingType.FREQUENCY

    def copy(self) -> "NextStrokeConfig":
        return replace(self)
