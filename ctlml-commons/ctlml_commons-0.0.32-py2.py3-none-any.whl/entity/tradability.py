from __future__ import annotations

from enum import Enum, auto


class Tradability(Enum):
    TRADABLE = auto()
    UNTRADABLE = auto()

    @staticmethod
    def to_enum(value: str) -> Tradability:
        v: str = value.upper().replace(" ", "-").replace("-", "_")
        return Tradability[v]

    def value(self) -> str:
        return self.name.lower()


def main() -> None:
    print(Tradability.to_enum("tradable"))
    print(Tradability.to_enum("untradable"))
    print(Tradability.TRADABLE.value())


if __name__ == "__main__":
    main()
