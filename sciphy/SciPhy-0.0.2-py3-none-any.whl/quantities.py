from physics.utils import *
from physics.errors import *
from typing import Union, Optional


class Quantity:
    __slots__ = ['_magnitude', '_unit']

    def __init__(self, magnitude: Union[int, float], unit: str):
        self._magnitude = magnitude
        self._unit = unit
        self._argscheck()

    def _argscheck(self):
        if not isinstance(self._magnitude, (int, float)) or not isinstance(self._unit, str):
            raise TypeError(f"Argument 'magnitude' must be of type 'int' or 'float' and 'unit' must be of type 'str'")
        if self.unit.strip() == '':
            raise ValueError(f"Argument 'unit' cannot be empty string")

    def __repr__(self):
        return f"<Quantity Obj: {self.magnitude} {self.unit}>"

    def __str__(self):
        return f"{self.magnitude} {self.unit}"

    def __add__(self, other):
        if not isinstance(other, (float, int, Quantity)):
            raise TypeError(f"unsupported operand type(s) for +: {classify(other)} and 'Quantity'")
        if isinstance(other, (int, float)):
            return Quantity(self.magnitude+other, self.unit)
        if other.unit != self.unit:
            raise UnitError(f"unsupported operand unit(s) for +: '{self.unit}' and '{other.unit}'")
        return Quantity(self.magnitude+other.magnitude, self.unit)

    def __sub__(self, other):
        if not isinstance(other, (float, int, Quantity)):
            raise TypeError(f"unsupported operand type(s) for -: {classify(other)} and 'Quantity'")
        if isinstance(other, (int, float)):
            return Quantity(self.magnitude-other, self.unit)
        if other.unit != self.unit:
            raise UnitError(f"unsupported operand unit(s) for -: '{self.unit}' and '{other.unit}'")
        return Quantity(self.magnitude-other.magnitude, self.unit)

    def __mul__(self, other):
        if not isinstance(other, (float, int, Quantity)):
            raise TypeError(f"unsupported operand type(s) for *: {classify(other)} and 'Quantity'")
        if isinstance(other, (int, float)):
            return Quantity(self.magnitude*other, self.unit)
        if other.unit != self.unit:
            raise UnitError(f"unsupported operand unit(s) for *: '{self.unit}' and '{other.unit}'")
        return Quantity(self.magnitude*other.magnitude, self.unit)

    def __truediv__(self, other):
        if not isinstance(other, (float, int, Quantity)):
            raise TypeError(f"unsupported operand type(s) for /: {classify(other)} and 'Quantity'")
        if isinstance(other, (int, float)):
            return Quantity(self.magnitude/other, self.unit)
        if other.unit != self.unit:
            raise UnitError(f"unsupported operand unit(s) for *: '{self.unit}' and '{other.unit}'")
        return Quantity(self.magnitude/other.magnitude, self.unit)

    def __floordiv__(self, other):
        if not isinstance(other, (float, int, Quantity)):
            raise TypeError(f"unsupported operand type(s) for //: {classify(other)} and 'Quantity'")
        if isinstance(other, (int, float)):
            return Quantity(self.magnitude // other, self.unit)
        if other.unit != self.unit:
            raise UnitError(f"unsupported operand unit(s) for *: '{self.unit}' and '{other.unit}'")
        return Quantity(self.magnitude // other.magnitude, self.unit)

    def __mod__(self, other):
        if not isinstance(other, (float, int, Quantity)):
            raise TypeError(f"unsupported operand type(s) for %: {classify(other)} and 'Quantity'")
        if isinstance(other, (int, float)):
            return Quantity(self.magnitude % other, self.unit)
        if other.unit != self.unit:
            raise UnitError(f"unsupported operand unit(s) for *: '{self.unit}' and '{other.unit}'")
        return Quantity(self.magnitude % other.magnitude, self.unit)

    def __eq__(self, other):
        if not isinstance(other, (float, int, Quantity)):
            raise TypeError(f"unsupported comparison type(s) for ==: {classify(other)} and 'Quantity'")
        if isinstance(other, (int, float)):
            return self.magnitude == other
        return other.unit == self.unit and other.magnitude == self.magnitude

    def __le__(self, other):
        if not isinstance(other, (float, int, Quantity)):
            raise TypeError(f"unsupported comparison type(s) for <=: {classify(other)} and 'Quantity'")
        if isinstance(other, (int, float)):
            return self.magnitude == other
        if other.unit != self.unit:
            raise UnitError(f"unsupported comparison unit(s) for <=: '{other.unit}' and '{self.unit}'")
        return other.magnitude == self.magnitude

    @property
    def magnitude(self) -> Union[int, float]:
        return self._magnitude

    @magnitude.setter
    def magnitude(self, _magnitude):
        if not isinstance(_magnitude, (int, float)):
            raise TypeError(f"magnitude must of type 'int' or 'float'")
        self._magnitude = _magnitude

    @property
    def unit(self) -> str:
        return self._unit

    @unit.setter
    def unit(self, _unit):
        if not isinstance(_unit, str):
            raise TypeError(f"unit must be of type 'str'")
        self._unit = _unit

