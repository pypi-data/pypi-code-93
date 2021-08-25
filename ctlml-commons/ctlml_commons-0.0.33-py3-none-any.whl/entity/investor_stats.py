from dataclasses import dataclass, field
from typing import List, Set

from ctlml_commons.entity.history import History


@dataclass
class Stats:
    num_transactions: int = 0
    starting_funds: float = 0
    history: List[History] = field(default_factory=list)
    symbols_held: Set[str] = field(default_factory=set)
