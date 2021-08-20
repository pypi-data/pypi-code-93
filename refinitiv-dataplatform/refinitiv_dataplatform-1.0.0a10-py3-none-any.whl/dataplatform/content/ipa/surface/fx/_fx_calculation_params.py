# coding: utf8
# contract_gen 2020-06-16 10:12:54.878244

__all__ = ["CalculationParams"]

from ...instrument._definition import ObjectDefinition
from ...enum_types.price_side import PriceSide
from ...enum_types.fx_swap_calculation_method import FxSwapCalculationMethod
from ...enum_types.fx_volatility_model import FxVolatilityModel
from ...enum_types.axis import Axis
from ...enum_types.time_stamp import TimeStamp
from ...models import BidAskMid
from ...models import InterpolationWeight


class CalculationParams(ObjectDefinition):
    def __init__(
        self,
        *,
        atm_volatility_object=None,
        butterfly10_d_object=None,
        butterfly25_d_object=None,
        domestic_deposit_rate_percent_object=None,
        foreign_deposit_rate_percent_object=None,
        forward_points_object=None,
        fx_spot_object=None,
        fx_swap_calculation_method=None,
        implied_volatility_object=None,
        interpolation_weight=None,
        price_side=None,
        risk_reversal10_d_object=None,
        risk_reversal25_d_object=None,
        time_stamp=None,
        volatility_model=None,
        x_axis,
        y_axis,
        calculation_date=None,
    ):
        super().__init__()
        self.atm_volatility_object = atm_volatility_object
        self.butterfly10_d_object = butterfly10_d_object
        self.butterfly25_d_object = butterfly25_d_object
        self.domestic_deposit_rate_percent_object = domestic_deposit_rate_percent_object
        self.foreign_deposit_rate_percent_object = foreign_deposit_rate_percent_object
        self.forward_points_object = forward_points_object
        self.fx_spot_object = fx_spot_object
        self.fx_swap_calculation_method = fx_swap_calculation_method
        self.implied_volatility_object = implied_volatility_object
        self.interpolation_weight = interpolation_weight
        self.price_side = price_side
        self.risk_reversal10_d_object = risk_reversal10_d_object
        self.risk_reversal25_d_object = risk_reversal25_d_object
        self.time_stamp = time_stamp
        self.volatility_model = volatility_model
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.calculation_date = calculation_date

    @property
    def atm_volatility_object(self):
        """
        At the money volatility at Expiry
        :return: object BidAskMid
        """
        return self._get_object_parameter(BidAskMid, "atmVolatilityObject")

    @atm_volatility_object.setter
    def atm_volatility_object(self, value):
        self._set_object_parameter(BidAskMid, "atmVolatilityObject", value)

    @property
    def butterfly10_d_object(self):
        """
        BF 10 Days at Expiry
        :return: object BidAskMid
        """
        return self._get_object_parameter(BidAskMid, "butterfly10DObject")

    @butterfly10_d_object.setter
    def butterfly10_d_object(self, value):
        self._set_object_parameter(BidAskMid, "butterfly10DObject", value)

    @property
    def butterfly25_d_object(self):
        """
        BF 25 Days at Expiry
        :return: object BidAskMid
        """
        return self._get_object_parameter(BidAskMid, "butterfly25DObject")

    @butterfly25_d_object.setter
    def butterfly25_d_object(self, value):
        self._set_object_parameter(BidAskMid, "butterfly25DObject", value)

    @property
    def domestic_deposit_rate_percent_object(self):
        """
        Domestic Deposit Rate at Expiry
        :return: object BidAskMid
        """
        return self._get_object_parameter(BidAskMid, "domesticDepositRatePercentObject")

    @domestic_deposit_rate_percent_object.setter
    def domestic_deposit_rate_percent_object(self, value):
        self._set_object_parameter(BidAskMid, "domesticDepositRatePercentObject", value)

    @property
    def foreign_deposit_rate_percent_object(self):
        """
        Foreign Deposit Rate at Expiry
        :return: object BidAskMid
        """
        return self._get_object_parameter(BidAskMid, "foreignDepositRatePercentObject")

    @foreign_deposit_rate_percent_object.setter
    def foreign_deposit_rate_percent_object(self, value):
        self._set_object_parameter(BidAskMid, "foreignDepositRatePercentObject", value)

    @property
    def forward_points_object(self):
        """
        Forward Points at Expiry
        :return: object BidAskMid
        """
        return self._get_object_parameter(BidAskMid, "forwardPointsObject")

    @forward_points_object.setter
    def forward_points_object(self, value):
        self._set_object_parameter(BidAskMid, "forwardPointsObject", value)

    @property
    def fx_spot_object(self):
        """
        Spot Price
        :return: object BidAskMid
        """
        return self._get_object_parameter(BidAskMid, "fxSpotObject")

    @fx_spot_object.setter
    def fx_spot_object(self, value):
        self._set_object_parameter(BidAskMid, "fxSpotObject", value)

    @property
    def fx_swap_calculation_method(self):
        """
        The method we chose to price outrights using or not implied deposits. Possible values are:

         FxSwap (compute outrights using swap points),

         DepositCcy1ImpliedFromFxSwap (compute currency1 deposits using swap points),

         DepositCcy2ImpliedFromFxSwap (compute currency2 deposits using swap points).

         Optional. Defaults to 'FxSwap'.
        :return: enum FxSwapCalculationMethod
        """
        return self._get_enum_parameter(
            FxSwapCalculationMethod, "fxSwapCalculationMethod"
        )

    @fx_swap_calculation_method.setter
    def fx_swap_calculation_method(self, value):
        self._set_enum_parameter(
            FxSwapCalculationMethod, "fxSwapCalculationMethod", value
        )

    @property
    def implied_volatility_object(self):
        """
        Implied Volatility at Expiry
        :return: object BidAskMid
        """
        return self._get_object_parameter(BidAskMid, "impliedVolatilityObject")

    @implied_volatility_object.setter
    def implied_volatility_object(self, value):
        self._set_object_parameter(BidAskMid, "impliedVolatilityObject", value)

    @property
    def interpolation_weight(self):
        """
        Vol Term Structure Interpolation
        :return: object InterpolationWeight
        """
        return self._get_object_parameter(InterpolationWeight, "interpolationWeight")

    @interpolation_weight.setter
    def interpolation_weight(self, value):
        self._set_object_parameter(InterpolationWeight, "interpolationWeight", value)

    @property
    def price_side(self):
        """
        Specifies whether bid, ask or mid is used to build the surface.
        :return: enum FxPriceSide
        """
        return self._get_enum_parameter(PriceSide, "priceSide")

    @price_side.setter
    def price_side(self, value):
        self._set_enum_parameter(PriceSide, "priceSide", value)

    @property
    def risk_reversal10_d_object(self):
        """
        RR 10 Days at Expiry
        :return: object BidAskMid
        """
        return self._get_object_parameter(BidAskMid, "riskReversal10DObject")

    @risk_reversal10_d_object.setter
    def risk_reversal10_d_object(self, value):
        self._set_object_parameter(BidAskMid, "riskReversal10DObject", value)

    @property
    def risk_reversal25_d_object(self):
        """
        RR 25 Days at Expiry
        :return: object BidAskMid
        """
        return self._get_object_parameter(BidAskMid, "riskReversal25DObject")

    @risk_reversal25_d_object.setter
    def risk_reversal25_d_object(self, value):
        self._set_object_parameter(BidAskMid, "riskReversal25DObject", value)

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
        :return: enum FxVolatilityModel
        """
        return self._get_enum_parameter(FxVolatilityModel, "volatilityModel")

    @volatility_model.setter
    def volatility_model(self, value):
        self._set_enum_parameter(FxVolatilityModel, "volatilityModel", value)

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
