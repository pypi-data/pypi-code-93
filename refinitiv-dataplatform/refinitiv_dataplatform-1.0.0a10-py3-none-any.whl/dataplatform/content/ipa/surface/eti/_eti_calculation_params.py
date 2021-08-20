# coding: utf8
# contract_gen 2020-06-16 10:12:54.865244

__all__ = ["CalculationParams"]

from ...enum_types.axis import Axis
from ...enum_types.eti_input_volatility_type import EtiInputVolatilityType
from ...enum_types.price_side import PriceSide
from ...enum_types.time_stamp import TimeStamp
from ...enum_types.volatility_model import VolatilityModel
from ...instrument._definition import ObjectDefinition


class CalculationParams(ObjectDefinition):
    def __init__(
        self,
        input_volatility_type=None,
        price_side=None,
        time_stamp=None,
        volatility_model=None,
        x_axis=None,
        y_axis=None,
        calculation_date=None,
    ):
        super().__init__()
        self.input_volatility_type = input_volatility_type
        self.price_side = price_side
        self.time_stamp = time_stamp
        self.volatility_model = volatility_model
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.calculation_date = calculation_date

    @property
    def input_volatility_type(self):
        """
        Specifies the type of volatility used as an input of the model (calculated Implied Volatility, Settlement)

         - Settle: [DEPRECATED] The service uses the settlement volatility to build the volatility surface

         - Quoted: The service uses the quoted volatility to build the volatility surface

         - Implied: The service internally calculates implied volatilities for the option universe before building the surface
        :return: enum EtiInputVolatilityType
        """
        return self._get_enum_parameter(EtiInputVolatilityType, "inputVolatilityType")

    @input_volatility_type.setter
    def input_volatility_type(self, value):
        self._set_enum_parameter(EtiInputVolatilityType, "inputVolatilityType", value)

    @property
    def price_side(self):
        """
        Specifies whether bid, ask or mid is used to build the surface.
        :return: enum PriceSide
        """
        return self._get_enum_parameter(PriceSide, "priceSide")

    @price_side.setter
    def price_side(self, value):
        self._set_enum_parameter(PriceSide, "priceSide", value)

    @property
    def time_stamp(self):
        """
        Define how the timestamp is selected:
        - Open: the opening value of the valuationDate or if not available the close of the previous day is used.
        - Default: the latest snapshot is used when valuationDate is today, the close price when valuationDate is in the past.
        :return: enum TimeStamp
        """
        return self._get_enum_parameter(TimeStamp, "timeStamp")

    @time_stamp.setter
    def time_stamp(self, value):
        self._set_enum_parameter(TimeStamp, "timeStamp", value)

    @property
    def volatility_model(self):
        """
        The quantitative model used to generate the volatility surface. This may depend on the asset class.
        For Fx Volatility Surface, we currently support the SVI model.
        :return: enum VolatilityModel
        """
        return self._get_enum_parameter(VolatilityModel, "volatilityModel")

    @volatility_model.setter
    def volatility_model(self, value):
        self._set_enum_parameter(VolatilityModel, "volatilityModel", value)

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
    def calculation_date(self):
        """
        The date the volatility surface is generated.
        :return: str
        """
        return self._get_parameter("calculationDate")

    @calculation_date.setter
    def calculation_date(self, value):
        self._set_parameter("calculationDate", value)
