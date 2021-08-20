# coding: utf8
# contract_gen 2020-06-16 10:26:10.715160

__all__ = ["Definition"]

from .._base_definition import BaseDefinition
from ._swaption_calculation_params import CalculationParams
from ...enum_types.discounting_type import DiscountingType
from ...instrument._definition import ObjectDefinition
from ...enum_types.underlying_type import UnderlyingType


class SwaptionUnderlyingDefinition(ObjectDefinition):
    def __init__(self, instrument_code=None, discounting_type=None):
        super().__init__()
        self.instrument_code = instrument_code
        self.discounting_type = discounting_type

    @property
    def discounting_type(self):
        """
        the discounting type of the IR vol model: OisDiscounting, or BorDiscounting (default)
        :return: enum DiscountingType
        """
        return self._get_enum_parameter(DiscountingType, "discountingType")

    @discounting_type.setter
    def discounting_type(self, value):
        self._set_enum_parameter(DiscountingType, "discountingType", value)

    @property
    def instrument_code(self):
        """
        The currency of the stripped cap surface, vol cube, or interest rate vol model
        :return: str
        """
        return self._get_parameter("instrumentCode")

    @instrument_code.setter
    def instrument_code(self, value):
        self._set_parameter("instrumentCode", value)


class Definition(BaseDefinition):
    def __init__(
        self,
        *,
        instrument_code=None,
        discounting_type=None,
        tag,
        layout,
        calculation_params,
    ):
        super().__init__(
            tag=tag, layout=layout, underlying_type=UnderlyingType.SWAPTION
        )
        self.calculation_params = calculation_params
        self.underlying_definition = SwaptionUnderlyingDefinition(
            instrument_code=instrument_code, discounting_type=discounting_type
        )

    @property
    def calculation_params(self):
        """
        The section that contains the properties that define how the volatility surface is generated
        :return: object EtiSurfaceParameters
        """
        return self._get_object_parameter(CalculationParams, "surfaceParameters")

    @calculation_params.setter
    def calculation_params(self, value):
        self._set_object_parameter(CalculationParams, "surfaceParameters", value)

    @property
    def underlying_definition(self):
        """
        The section that contains the properties that define the underlying instrument
        :return: object EtiSurfaceDefinition
        """
        return self._get_object_parameter(
            SwaptionUnderlyingDefinition, "underlyingDefinition"
        )

    @underlying_definition.setter
    def underlying_definition(self, value):
        self._set_object_parameter(
            SwaptionUnderlyingDefinition, "underlyingDefinition", value
        )
