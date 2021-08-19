from dataclasses import dataclass


@dataclass(frozen=True)
class Popularity:
    instrument: str
    num_open_positions: int
    symbol: str
