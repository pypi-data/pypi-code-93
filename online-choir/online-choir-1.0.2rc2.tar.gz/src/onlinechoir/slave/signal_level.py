import numpy as np
from enum import IntEnum

from ..common.constants import SATURATION_LEVEL


class SignalLevel(IntEnum):
    white = -1
    grey = 0
    green = 1
    orange = 2
    red = 3

    @classmethod
    def from_dbs(cls, dbs: float, pp: float):
        if pp >= 1:
            return SignalLevel.red
        elif dbs >= -3:
            return SignalLevel.orange
        elif dbs >= -9:
            return SignalLevel.green
        return SignalLevel.grey

    @classmethod
    def from_chunk(cls, chunk: np.ndarray):
        pp = np.abs(chunk).max()
        if pp >= SATURATION_LEVEL:  # save some calculations
            return SignalLevel.red
        return cls.from_dbs(cls.calculate_dbs(chunk), pp)

    @staticmethod
    def calculate_dbs(chunk: np.ndarray) -> float:
        var = chunk.var()  # signal can clip if var > 0.1111, therefore we set the 0dB to 0.1111.
        if var == 0:
            return -100.
        return 10 * np.log10(9 * var)
