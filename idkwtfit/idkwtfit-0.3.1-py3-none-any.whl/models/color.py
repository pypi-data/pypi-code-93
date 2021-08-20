from typing import NamedTuple


class RGB(NamedTuple):
    R: int
    G: int
    B: int


class HSL(NamedTuple):
    H: int
    S: int
    L: int


class CMYK(NamedTuple):
    C: int
    M: int
    Y: int
    K: int
