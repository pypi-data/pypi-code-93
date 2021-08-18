#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel Array class."""

import typing as t  # noqa: F401

import numpy as np
from astropy.units import cds

from pyxel.util.memory import get_size

# TODO: Is it possible to move this to `data_structure/__init__.py' ?
cds.enable()


# TODO: Does it make sense to force 'self._array' to be read-only ?
#       It could be done with:
#       ... self._array = np.array(value)
#       ... self._array.setflags(write=False)
class Array:
    """Array class."""

    EXP_TYPE = type(None)  # type: t.Type
    TYPE_LIST = ()  # type: t.Tuple[t.Type, ...]

    # TODO: Add units ?
    def __init__(self, value: np.ndarray):
        self.validate_type(value)

        self._array = value  # type: np.ndarray

        self._numbytes = 0

        # TODO: is `self.type` needed ?
        # self.type = None            # type: t.Optional[type]

        # TODO: Implement a method to initialized 'self._array' ???

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        shape = self._array.shape
        dtype = self._array.dtype

        return f"{cls_name}<shape={shape}, dtype={dtype}>"

    def validate_type(self, value: np.ndarray) -> None:
        """Validate a value.

        Parameters
        ----------
        value
        """
        cls_name = self.__class__.__name__  # type: str

        if not isinstance(value, np.ndarray):
            raise TypeError(f"{cls_name} array should be a numpy.ndarray")

        if value.dtype not in self.TYPE_LIST:
            exp_type_name = self.EXP_TYPE.__name__  # type: str
            raise TypeError(f"Expected type of {cls_name} array is {exp_type_name}.")

    def validate_shape(self, value: np.ndarray) -> None:
        """TBW."""
        cls_name = self.__class__.__name__  # type: str

        if value.shape != self._array.shape:
            raise ValueError(f"Expected {cls_name} array is {self._array.shape}.")

    @property
    def array(self) -> np.ndarray:
        """Two dimensional numpy array storing the data.

        Only accepts an array with the right type and shape.
        """
        # if self._array is None:
        #     raise ValueError("'array' is not initialized.")

        return self._array

    @array.setter
    def array(self, value: np.ndarray) -> None:
        """Overwrite the two dimensional numpy array storing the data.

        Only accepts an array with the right type and shape.
        """
        self.validate_type(value)
        self.validate_shape(value)

        # self.type = value.dtype
        self._array = value

    # TODO: Is it necessary ? Maybe not if you implement method __array__
    @property
    def mean(self) -> float:
        """Return mean of all pixel values."""
        return float(np.mean(self._array))

    @property
    def std_deviation(self) -> float:
        """Return standard deviation of all pixel values."""
        return float(np.std(self._array))

    @property
    def max(self) -> float:
        """Return maximum of all pixel values."""
        return float(np.max(self._array))

    @property
    def min(self) -> float:
        """Return minimum of all pixel values."""
        return float(np.min(self._array))

    @property
    def peak_to_peak(self) -> float:
        """Return peak-to-peak value of all pixel values."""
        return float(np.ptp(self._array))

    @property
    def sum(self) -> float:
        """Return sum of all pixel values."""
        return float(np.sum(self._array))

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
