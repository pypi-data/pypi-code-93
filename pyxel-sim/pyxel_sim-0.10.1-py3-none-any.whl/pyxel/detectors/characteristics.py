#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""
import typing as t

import numpy as np

from pyxel.util.memory import get_size


# TODO: 'vg' should be the full volume and not the half
class Characteristics:
    """Characteristical attributes of the detector."""

    def __init__(
        self,
        qe: float = 0.0,  # unit: NA
        eta: float = 0.0,  # unit: electron/photon
        sv: float = 0.0,  # unit: volt/electron
        amp: float = 0.0,  # unit: V/V
        a1: float = 0.0,  # unit: V/V
        a2: int = 0,  # unit: adu/V
        fwc: int = 0,  # unit: electron
        vg: float = 0.0,  # unit: cm^2
        dt: float = 0.0,  # unit: s
    ):
        """Create an instance of `Characteristics`.

        Parameters
        ----------
        qe: float
            Quantum efficiency.
        eta: float
            Quantum yield. Unit: e-/photon
        sv: float
            Sensitivity of charge readout. Unit: V/e-
        amp: float
            Gain of output amplifier. Unit: V/V
        a1: float
            Gain of the signal processor. Unit: V/V
        a2: int
            Gain of the Analog-Digital Converter. Unit: ADU/V
        fwc: int
            Full well capacity. Unit: e-
        vg: float
            Half pixel volume charge can occupy. Unit: cm^2
        dt: float
            Pixel dwell time. Unit: s
        """
        if not (0.0 <= qe <= 1.0):
            raise ValueError("'qe' must be between 0.0 and 1.0.")

        if not (0.0 <= eta <= 1.0):
            raise ValueError("'eta' must be between 0.0 and 1.0.")

        if not (0.0 <= sv <= 100.0):
            raise ValueError("'sv' must be between 0.0 and 100.0.")

        if not (0.0 <= amp <= 100.0):
            raise ValueError("'amp' must be between 0.0 and 100.0.")

        if not (0.0 <= a1 <= 100.0):
            raise ValueError("'a1' must be between 0.0 and 100.0.")

        if a2 not in range(65537):
            raise ValueError("'a2' must be between 0 and 65536.")

        if fwc not in range(10000001):
            raise ValueError("'fwc' must be between 0 and 1e+7.")

        if not (0.0 <= vg <= 1.0):
            raise ValueError("'vg' must be between 0.0 and 1.0.")

        if not (0.0 <= dt <= 10.0):
            raise ValueError("'dt' must be between 0.0 and 10.0.")

        self._qe = qe  # type: t.Union[float, np.ndarray]
        self._eta = eta
        self._sv = sv
        self._amp = amp
        self._a1 = a1
        self._a2 = a2
        self._fwc = fwc
        self._vg = vg
        self._dt = dt

        self._numbytes = 0

    @property
    def qe(self) -> t.Union[float, np.ndarray]:
        """Get Quantum efficiency."""
        return self._qe

    @qe.setter
    def qe(self, value: t.Union[float, np.ndarray]) -> None:
        """Set Quantum efficiency."""
        if not (0.0 <= np.min(value)) and (np.max(value) <= 1.0):
            raise ValueError("'QE' values must be between 0.0 and 1.0.")

        self._qe = value

    @property
    def eta(self) -> float:
        """Get Quantum yield."""
        return self._eta

    @eta.setter
    def eta(self, value: float) -> None:
        """Set Quantum yield."""
        if not (0.0 <= value <= 1.0):
            raise ValueError("'eta' must be between 0.0 and 1.0.")

        self._eta = value

    @property
    def sv(self) -> float:
        """Get Sensitivity of charge readout."""
        return self._sv

    @sv.setter
    def sv(self, value: float) -> None:
        """Set Sensitivity of charge readout."""
        if not (0.0 <= value <= 100.0):
            raise ValueError("'sv' must be between 0.0 and 100.0.")
        self._sv = value

    @property
    def amp(self) -> float:
        """Get Gain of output amplifier."""
        return self._amp

    @amp.setter
    def amp(self, value: float) -> None:
        """Set Gain of output amplifier."""
        if not (0.0 <= value <= 100.0):
            raise ValueError("'amp' must be between 0.0 and 100.0.")

        self._amp = value

    @property
    def a1(self) -> float:
        """Get Gain of the signal processor."""
        return self._a1

    @a1.setter
    def a1(self, value: float) -> None:
        """Set Gain of the signal processor."""
        if not (0.0 <= value <= 100.0):
            raise ValueError("'a1' must be between 0.0 and 100.0.")

        self._a1 = value

    @property
    def a2(self) -> int:
        """Get Gain of the Analog-Digital Converter."""
        return self._a2

    @a2.setter
    def a2(self, value: int) -> None:
        """Set Gain of the Analog-Digital Converter."""
        if value not in range(65537):
            raise ValueError("'a2' must be between 0 and 65536.")

        self._a2 = value

    @property
    def fwc(self) -> int:
        """Get Full well capacity."""
        return self._fwc

    @fwc.setter
    def fwc(self, value: int) -> None:
        """Set Full well capacity."""
        if value not in range(10000001):
            raise ValueError("'fwc' must be between 0 and 1e+7.")

        self._fwc = value

    @property
    def vg(self) -> float:
        """Get Half pixel volume charge can occupy."""
        return self._vg

    @vg.setter
    def vg(self, value: float) -> None:
        """Set Half pixel volume charge can occupy."""
        if not (0.0 <= value <= 1.0):
            raise ValueError("'vg' must be between 0.0 and 1.0.")

    @property
    def dt(self) -> float:
        """Get Pixel dwell time."""
        return self._dt

    @dt.setter
    def dt(self, value: float) -> None:
        """Set Pixel dwell time."""
        if not (0.0 <= value <= 10.0):
            raise ValueError("'dt' must be between 0.0 and 10.0.")

        self._dt = value

    @property
    def numbytes(self) -> int:
        """Recursively calculates object size in bytes using Pympler library.

        Returns
        -------
        int
            Size of the object in bytes.
        """
        self._numbytes = get_size(self)
        return self._numbytes
