from __future__ import annotations

from enum import Enum, auto
from typing import Dict


class TimeInForce(Enum):
    GOOD_TIL_CANCELLED = auto()
    GOOD_FOR_THE_DAY = auto()
    IMMEDIATE_OR_CANCEL = auto()
    EXECUTE_AT_OPENING = auto()

    @classmethod
    def mapping(cls) -> Dict[str, TimeInForce]:
        return {
            "gtc": TimeInForce.GOOD_TIL_CANCELLED,
            "gfd": TimeInForce.GOOD_FOR_THE_DAY,
            "ioc": TimeInForce.IMMEDIATE_OR_CANCEL,
            "opg": TimeInForce.EXECUTE_AT_OPENING,
        }

    @classmethod
    def reverse_mapping(cls) -> Dict[TimeInForce, str]:
        return {v: k for k, v in TimeInForce.mapping().items()}

    @staticmethod
    def to_enum(value: str) -> TimeInForce:
        return TimeInForce.mapping()[value.lower()]

    def value(self) -> str:
        return TimeInForce.from_enum(value=self)

    @classmethod
    def from_enum(cls, value: TimeInForce) -> str:
        return TimeInForce.reverse_mapping()[value]


def main() -> None:
    print(TimeInForce.to_enum("gtc"))
    print(TimeInForce.from_enum(TimeInForce.EXECUTE_AT_OPENING))


if __name__ == "__main__":
    main()
