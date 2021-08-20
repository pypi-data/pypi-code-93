# coding: utf8
# contract_gen 2020-06-16 10:26:10.713160


__all__ = ["CalculationParams"]

from ...enum_types.input_volatility_type import InputVolatilityType
from ...enum_types.volatility_adjustment_type import VolatilityAdjustmentType
from ...enum_types.axis import Axis
from ...instrument._definition import ObjectDefinition


class CalculationParams(ObjectDefinition):
    def __init__(
        self,
        input_volatility_type=None,
        volatility_adjustment_type=None,
        x_axis=None,
        y_axis=None,
        z_axis=None,
        market_data_date=None,
        shift_percent=None,
        source=None,
        valuation_date=None,
    ):
        super().__init__()
        self.input_volatility_type = input_volatility_type
        self.volatility_adjustment_type = volatility_adjustment_type
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.z_axis = z_axis
        self.market_data_date = market_data_date
        self.shift_percent = shift_percent
        self.source = source
        self.valuation_date = valuation_date

    @property
    def input_volatility_type(self):
        """
        :return: enum InputVolatilityType
        """
        return self._get_enum_parameter(InputVolatilityType, "inputVolatilityType")

    @input_volatility_type.setter
    def input_volatility_type(self, value):
        self._set_enum_parameter(InputVolatilityType, "inputVolatilityType", value)

    @property
    def volatility_adjustment_type(self):
        """
        Volatility Adjustment method for stripping: ConstantCaplet, ConstantCap, ShiftedCap, NormalizedCap, NormalizedCaplet
        :return: enum VolatilityAdjustmentType
        """
        return self._get_enum_parameter(
            VolatilityAdjustmentType, "volatilityAdjustmentType"
        )

    @volatility_adjustment_type.setter
    def volatility_adjustment_type(self, value):
        self._set_enum_parameter(
            VolatilityAdjustmentType, "volatilityAdjustmentType", value
        )

    @property
    def x_axis(self):
        """
        Specifies the unit for the x axis (e.g. Date, Tenor)
        :return: enum Axis
        """
        return self._get_enum_parameter(Axis, "xAxis")

    @x_axis.setter
    def x_axis(self, value):
        self._set_enum_parameter(Axis, "xAxis", value)

    @property
    def y_axis(self):
        """
        Specifies the unit for the y axis (e.g. Strike, Delta). This may depend on the asset class.
        For Fx Volatility Surface, we support both Delta and Strike.
        :return: enum Axis
        """
        return self._get_enum_parameter(Axis, "yAxis")

    @y_axis.setter
    def y_axis(self, value):
        self._set_enum_parameter(Axis, "yAxis", value)

    @property
    def z_axis(self):
        """
        Specifies the unit for the z axis (e.g. Strike, Tenor, Expiries). This applies on Ir SABR Volatility Cube.
        :return: enum Axis
        """
        return self._get_enum_parameter(Axis, "zAxis")

    @z_axis.setter
    def z_axis(self, value):
        self._set_enum_parameter(Axis, "zAxis", value)

    @property
    def market_data_date(self):
        """
        :return: str
        """
        return self._get_parameter("marketDataDate")

    @market_data_date.setter
    def market_data_date(self, value):
        self._set_parameter("marketDataDate", value)

    @property
    def shift_percent(self):
        """
        Shift value to use in calibration(Strike/Forward). Default: 0.0
        :return: float
        """
        return self._get_parameter("shiftPercent")

    @shift_percent.setter
    def shift_percent(self, value):
        self._set_parameter("shiftPercent", value)

    @property
    def source(self):
        """
        Requested volatility data contributor.
        :return: str
        """
        return self._get_parameter("source")

    @source.setter
    def source(self, value):
        self._set_parameter("source", value)

    @property
    def valuation_date(self):
        """
        :return: str
        """
        return self._get_parameter("valuationDate")

    @valuation_date.setter
    def valuation_date(self, value):
        self._set_parameter("valuationDate", value)
