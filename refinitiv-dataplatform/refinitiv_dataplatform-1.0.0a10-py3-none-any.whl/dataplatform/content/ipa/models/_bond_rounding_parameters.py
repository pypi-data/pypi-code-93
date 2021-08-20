# coding: utf8
# contract_gen 2020-05-19 11:24:17.125186

__all__ = ["BondRoundingParameters"]

from ..instrument._definition import ObjectDefinition
from ..enum_types.rounding_type import RoundingType
from ..enum_types.rounding import Rounding


class BondRoundingParameters(ObjectDefinition):
    def __init__(
        self,
        accrued_rounding=None,
        accrued_rounding_type=None,
        price_rounding=None,
        price_rounding_type=None,
        spread_rounding=None,
        spread_rounding_type=None,
        yield_rounding=None,
        yield_rounding_type=None,
    ):
        super().__init__()
        self.accrued_rounding = accrued_rounding
        self.accrued_rounding_type = accrued_rounding_type
        self.price_rounding = price_rounding
        self.price_rounding_type = price_rounding_type
        self.spread_rounding = spread_rounding
        self.spread_rounding_type = spread_rounding_type
        self.yield_rounding = yield_rounding
        self.yield_rounding_type = yield_rounding_type

    @property
    def accrued_rounding(self):
        """
        Number of digits to apply for rounding of Accrued field. Available values are Zero, One, Two,..., Eight, Default, Unrounded.
        Optional. A default value may be defined in bond reference data, in that case it is used. If it is not the case no rounding is applied.
        :return: enum Rounding
        """
        return self._get_enum_parameter(Rounding, "accruedRounding")

    @accrued_rounding.setter
    def accrued_rounding(self, value):
        self._set_enum_parameter(Rounding, "accruedRounding", value)

    @property
    def accrued_rounding_type(self):
        """
        Type of rounding for accrued rounding.
        Optional. A default value can be defined in bond reference data. Otherwise, default value is Near.
        :return: enum RoundingType
        """
        return self._get_enum_parameter(RoundingType, "accruedRoundingType")

    @accrued_rounding_type.setter
    def accrued_rounding_type(self, value):
        self._set_enum_parameter(RoundingType, "accruedRoundingType", value)

    @property
    def price_rounding(self):
        """
        Number of digits to apply for price rounding. Available values are Zero, One, Two,..., Eight, Default, Unrounded.
        Optional. A default value may be defined in bond reference data, in that case it is used. If it is not the case no rounding is applied.
        :return: enum Rounding
        """
        return self._get_enum_parameter(Rounding, "priceRounding")

    @price_rounding.setter
    def price_rounding(self, value):
        self._set_enum_parameter(Rounding, "priceRounding", value)

    @property
    def price_rounding_type(self):
        """
        Type of rounding for price rounding.
        Optional. A default value can be defined in bond reference data. Otherwise, default value is Near.
        :return: enum RoundingType
        """
        return self._get_enum_parameter(RoundingType, "priceRoundingType")

    @price_rounding_type.setter
    def price_rounding_type(self, value):
        self._set_enum_parameter(RoundingType, "priceRoundingType", value)

    @property
    def spread_rounding(self):
        """
        Number of digits to apply for spread rounding. Available values are Zero, One, Two,..., Eight, Default, Unrounded.
        Note that spread rounding is done directly on the base point value.
        Optional. By default, data from the bond structure.
        :return: enum Rounding
        """
        return self._get_enum_parameter(Rounding, "spreadRounding")

    @spread_rounding.setter
    def spread_rounding(self, value):
        self._set_enum_parameter(Rounding, "spreadRounding", value)

    @property
    def spread_rounding_type(self):
        """
        :return: enum RoundingType
        """
        return self._get_enum_parameter(RoundingType, "spreadRoundingType")

    @spread_rounding_type.setter
    def spread_rounding_type(self, value):
        self._set_enum_parameter(RoundingType, "spreadRoundingType", value)

    @property
    def yield_rounding(self):
        """
        Number of digits to apply for yield rounding. Available values are Zero, One, Two,..., Eight, Default, Unrounded.
        Optional. A default value may be defined in bond reference data, in that case it is used. If it is not the case no rounding is applied.
        :return: enum Rounding
        """
        return self._get_enum_parameter(Rounding, "yieldRounding")

    @yield_rounding.setter
    def yield_rounding(self, value):
        self._set_enum_parameter(Rounding, "yieldRounding", value)

    @property
    def yield_rounding_type(self):
        """
        Type of rounding for yield rounding.
        Optional. A default value can be defined in bond reference data. Otherwise, default value is Near.
        :return: enum RoundingType
        """
        return self._get_enum_parameter(RoundingType, "yieldRoundingType")

    @yield_rounding_type.setter
    def yield_rounding_type(self, value):
        self._set_enum_parameter(RoundingType, "yieldRoundingType", value)
