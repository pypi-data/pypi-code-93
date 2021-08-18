#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""

from pyxel.util.memory import get_size


class Environment:
    """Environmental attributes of the detector."""

    def __init__(
        self,
        temperature: float = 273.15,
        total_ionising_dose: float = 0.0,
        total_non_ionising_dose: float = 0.0,
    ):
        """Create a new instance of `Environment`.

        Parameters
        ----------
        temperature: float
            Temperature of the detector. Unit: K
        total_ionising_dose: float
            Total Ionising Dose (TID) of the detector. Unit: MeV/g
        total_non_ionising_dose: float
            Total Non-Ionising Dose (TNID) of the detector. Unit: MeV/g
        """
        if not (0.0 <= temperature <= 1000.0):
            raise ValueError("'temperature' must be between 0.0 and 1000.0.")

        if not (0.0 <= total_ionising_dose <= 1e15):
            raise ValueError("'total_ionising_dose' must be between 0.0 and 1e15.")

        if not (0.0 <= total_non_ionising_dose <= 1e15):
            raise ValueError("'total_non_ionising_dose' must be between 0.0 and 1e15.")

        self._temperature = temperature
        self._total_ionising_dose = total_ionising_dose
        self._total_non_ionising_dose = total_non_ionising_dose

        self._numbytes = 0

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__  # type: str
        return (
            f"{cls_name}(temperature={self._temperature!r}, "
            f"total_ionising_dose={self._total_ionising_dose!r}, "
            f"total_non_ionising_dose={self._total_non_ionising_dose!r})"
        )

    @property
    def temperature(self) -> float:
        """Get Temperature of the detector."""
        return self._temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        """Set Temperature of the detector."""
        if not (0.0 <= value <= 1000.0):
            raise ValueError("'temperature' must be between 0.0 and 1000.0.")

        self._temperature = value

    @property
    def total_ionising_dose(self) -> float:
        """Get Total Ionising Dose (TID) of the detector."""
        return self._total_ionising_dose

    @total_ionising_dose.setter
    def total_ionising_dose(self, value: float) -> None:
        """Set Total Ionising Dose (TID) of the detector."""
        if not (0.0 <= value <= 1e15):
            raise ValueError("'total_ionising_dose' must be between 0.0 and 1e15.")

        self._total_ionising_dose = value

    @property
    def total_non_ionising_dose(self) -> float:
        """Get Total Ionising Dose (TID) of the detector."""
        return self._total_non_ionising_dose

    @total_non_ionising_dose.setter
    def total_non_ionising_dose(self, value: float) -> None:
        """Set Total Ionising Dose (TID) of the detector."""
        if not (0.0 <= value <= 1e15):
            raise ValueError("'total_non_ionising_dose' must be between 0.0 and 1e15.")

        self._total_non_ionising_dose = value

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
