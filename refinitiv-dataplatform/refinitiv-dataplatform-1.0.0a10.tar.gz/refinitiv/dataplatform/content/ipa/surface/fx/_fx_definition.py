# coding: utf8
# contract_gen 2020-06-16 10:12:54.877244

__all__ = ["Definition"]

from ._fx_calculation_params import CalculationParams
from .._base_definition import BaseDefinition
from ...enum_types.underlying_type import UnderlyingType
from ...instrument._definition import ObjectDefinition


class FxUnderlyingDefinition(ObjectDefinition):
    def __init__(self, fx_cross_code):
        super().__init__()
        self.fx_cross_code = fx_cross_code

    @property
    def fx_cross_code(self):
        """
        The ISO code of the cross currency (e.g. 'EURCHF').
        Mandatory.
        :return: str
        """
        return self._get_parameter("fxCrossCode")

    @fx_cross_code.setter
    def fx_cross_code(self, value):
        self._set_parameter("fxCrossCode", value)


class Definition(BaseDefinition):
    def __init__(self, fx_cross_code, tag, layout, calculation_params):
        super().__init__(tag=tag, layout=layout, underlying_type=UnderlyingType.FX)
        self.calculation_params = calculation_params
        self.underlying_definition = FxUnderlyingDefinition(fx_cross_code=fx_cross_code)

    @property
    def calculation_params(self):
        """
        The section that contains the properties that define how the volatility surface is generated
        :return: object CalculationParams
        """
        return self._get_object_parameter(CalculationParams, "surfaceParameters")

    @calculation_params.setter
    def calculation_params(self, value):
        self._set_object_parameter(CalculationParams, "surfaceParameters", value)

    @property
    def underlying_definition(self):
        """
        The section that contains the properties that define the underlying instrument
        :return: object FxVolatilitySurfaceDefinition
        """
        return self._get_object_parameter(
            FxUnderlyingDefinition, "underlyingDefinition"
        )

    @underlying_definition.setter
    def underlying_definition(self, value):
        self._set_object_parameter(
            FxUnderlyingDefinition, "underlyingDefinition", value
        )
