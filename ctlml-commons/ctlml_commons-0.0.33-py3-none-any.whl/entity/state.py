from __future__ import annotations

from enum import Enum, auto
from typing import Optional


class State(Enum):
    ACTIVE = auto()  # In progress
    CANCELLED = auto()  # Cancelled
    COMPLETED = auto()  # Completed
    CONFIRMED = auto()  # Request confirmed, but not completed
    FAILED = auto()  # Failed
    FILLED = auto()  # TODO: same as completed? execution as been filled
    INVALID = auto()  # Invalid state, e.g. unable to execute.
    MISSING = auto()  # Missing state
    NO_OP = auto()  # Testing purposeful no-operation
    PARTIALLY_FILLED = auto()  # Request has been partially completed
    PENDING = auto()  # Pending execution
    QUEUED = auto()  # TODO: Queued for pending?
    SUBMITTED = auto()  # TODO: Submitted to be queued?
    UNCONFIRMED = auto()  # Unknown?
    UNKNOWN = auto()  # Unknown
    ALL = auto()  # All others

    @staticmethod
    def to_enum(value: str) -> Optional[State]:
        if value is None:
            return State.UNKNOWN
        v: str = value.upper().replace(" ", "-").replace("-", "_")
        return State[v]

    def value(self) -> str:
        return self.name.lower()
