# coding: utf8

__all__ = ["CalculationParams"]

from refinitiv.dataplatform.content.ipa.instrument import InstrumentCalculationParams


class CalculationParams(InstrumentCalculationParams):
    """
    Option pricing parameters
    """

    def __init__(
        self,
        atm_volatility_object=None,
        butterfly_10d_object=None,
        butterfly_25d_object=None,
        cutoff_time=None,
        cutoff_time_zone=None,
        domestic_deposit_rate_percent_object=None,
        foreign_deposit_rate_percent_object=None,
        forward_points_object=None,
        fx_spot_object=None,
        fx_swap_calculation_method=None,
        implied_volatility_object=None,
        interpolation_weight=None,
        market_value_in_deal_ccy=None,
        option_price_side=None,
        option_time_stamp=None,
        price_side=None,
        pricing_model_type=None,
        risk_free_rate_percent=None,
        risk_reversal_10d_object=None,
        risk_reversal_25d_object=None,
        underlying_price=None,
        underlying_price_side=None,
        underlying_time_stamp=None,
        valuation_date=None,
        volatility_model=None,
        volatility_percent=None,
        volatility_type=None,
        market_data_date=None,
    ):
        super().__init__()
        self.atm_volatility_object = atm_volatility_object
        self.butterfly_10d_object = butterfly_10d_object
        self.butterfly_25d_object = butterfly_25d_object
        self.cutoff_time = cutoff_time
        self.cutoff_time_zone = cutoff_time_zone
        self.domestic_deposit_rate_percent_object = domestic_deposit_rate_percent_object
        self.foreign_deposit_rate_percent_object = foreign_deposit_rate_percent_object
        self.forward_points_object = forward_points_object
        self.fx_spot_object = fx_spot_object
        self.fx_swap_calculation_method = fx_swap_calculation_method
        self.implied_volatility_object = implied_volatility_object
        self.interpolation_weight = interpolation_weight
        self.market_value_in_deal_ccy = market_value_in_deal_ccy
        self.option_price_side = option_price_side
        self.option_time_stamp = option_time_stamp
        self.price_side = price_side
        self.pricing_model_type = pricing_model_type
        self.risk_free_rate_percent = risk_free_rate_percent
        self.risk_reversal_10d_object = risk_reversal_10d_object
        self.risk_reversal_25d_object = risk_reversal_25d_object
        self.underlying_price = underlying_price
        self.underlying_price_side = underlying_price_side
        self.underlying_time_stamp = underlying_time_stamp
        self.valuation_date = valuation_date
        self.volatility_model = volatility_model
        self.volatility_percent = volatility_percent
        self.volatility_type = volatility_type
        self.market_data_date = market_data_date
        # self.compute_payout_chart = compute_payout_chart
        # self.compute_volatility_payout = compute_volatility_payout
        # self.payout_custom_dates = payout_custom_dates
        # self.payout_scaling_interval = payout_scaling_interval

    ###########################################
    # PricingParameters properties
    ###########################################
    @property
    def atm_volatility_object(self):
        """
        At the money volatility at Expiry
        :return: BidAskMid
        """
        from refinitiv.dataplatform.content.ipa.models import BidAskMid

        return self._get_object_parameter(BidAskMid, "atmVolatilityObject")

    @atm_volatility_object.setter
    def atm_volatility_object(self, value):
        from refinitiv.dataplatform.content.ipa.models import BidAskMid

        self._set_object_parameter(BidAskMid, "atmVolatilityObject", value)

    @property
    def butterfly_10d_object(self):
        """
        :return: float
        """
        return self._get_parameter("butterfly10DObject")

    @butterfly_10d_object.setter
    def butterfly_10d_object(self, value):
        self._set_parameter("butterfly10DObject", value)

    @property
    def butterfly_25d_object(self):
        """
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("butterfly25DObject")

    @butterfly_25d_object.setter
    def butterfly_25d_object(self, value):
        self._set_parameter("butterfly25DObject", value)

    @property
    def cutoff_time(self):
        """
        The cutoff time
        :return: string
        """
        return self._get_parameter("cutoffTime")

    @cutoff_time.setter
    def cutoff_time(self, value):
        self._set_parameter("cutoffTime", value)

    @property
    def cutoff_time_zone(self):
        """
        The cutoff time zone
        :return: string
        """
        return self._get_parameter("cutoffTimeZone")

    @cutoff_time_zone.setter
    def cutoff_time_zone(self, value):
        self._set_parameter("cutoffTimeZone", value)

    @property
    def domestic_deposit_rate_percent_object(self):
        """
        :return: BidAskMid
        """
        from refinitiv.dataplatform.content.ipa.models import BidAskMid

        return self._get_object_parameter(BidAskMid, "domesticDepositRatePercentObject")

    @domestic_deposit_rate_percent_object.setter
    def domestic_deposit_rate_percent_object(self, value):
        from refinitiv.dataplatform.content.ipa.models import BidAskMid

        self._set_object_parameter(BidAskMid, "domesticDepositRatePercentObject", value)

    @property
    def foreign_deposit_rate_percent_object(self):
        """
        :return: float
        """
        from refinitiv.dataplatform.content.ipa.models import BidAskMid

        return self._get_object_parameter(BidAskMid, "foreignDepositRatePercentObject")

    @foreign_deposit_rate_percent_object.setter
    def foreign_deposit_rate_percent_object(self, value):
        from refinitiv.dataplatform.content.ipa.models import BidAskMid

        self._set_object_parameter(BidAskMid, "foreignDepositRatePercentObject", value)

    @property
    def forward_points_object(self):
        """
        :return: float
        """
        from refinitiv.dataplatform.content.ipa.models import BidAskMid

        return self._get_object_parameter(BidAskMid, "forwdardPointsObject")

    @forward_points_object.setter
    def forward_points_object(self, value):
        from refinitiv.dataplatform.content.ipa.models import BidAskMid

        self._set_object_parameter(BidAskMid, "forwdardPointsObject", value)

    @property
    def fx_spot_object(self):
        """
        :return: float
        """
        from refinitiv.dataplatform.content.ipa.models import BidAskMid

        return self._get_object_parameter(BidAskMid, "fxSpotObject")

    @fx_spot_object.setter
    def fx_spot_object(self, value):
        from refinitiv.dataplatform.content.ipa.models import BidAskMid

        self._set_object_parameter(BidAskMid, "fxSpotObject", value)

    @property
    def fx_swap_calculation_method(self):
        """
        :return: string
        """
        return self._get_parameter("fxSwapCalculationMethod")

    @fx_swap_calculation_method.setter
    def fx_swap_calculation_method(self, value):
        self._set_parameter("fxSwapCalculationMethod", value)

    @property
    def implied_volatility_object(self):
        """
        :return: BidAskMid
        """
        from refinitiv.dataplatform.content.ipa.models import BidAskMid

        return self._get_object_parameter(BidAskMid, "impliedVolatilityObject")

    @implied_volatility_object.setter
    def implied_volatility_object(self, value):
        from refinitiv.dataplatform.content.ipa.models import BidAskMid

        self._set_object_parameter(BidAskMid, "impliedVolatilityObject", value)

    @property
    def interpolation_weight(self):
        """
        :return: InterpolationWeight
        """
        from refinitiv.dataplatform.content.ipa.models import InterpolationWeight

        return self._get_object_parameter(InterpolationWeight, "interpolationWeight")

    @interpolation_weight.setter
    def interpolation_weight(self, value):
        from refinitiv.dataplatform.content.ipa.models import InterpolationWeight

        self._set_object_parameter(InterpolationWeight, "interpolationWeight", value)

    @property
    def market_value_in_deal_ccy(self):
        """
        MarketValueInDealCcy to override and that will be used as pricing analysis input to compute VolatilityPercent.
        Optional. No override is applied by default. Note that Premium takes priority over Volatility input.
        :return: float
        """
        return self._get_parameter("marketValueInDealCcy")

    @market_value_in_deal_ccy.setter
    def market_value_in_deal_ccy(self, value):
        self._set_parameter("marketValueInDealCcy", value)

    @property
    def option_price_side(self):
        """
        :return: PriceSide
        """
        from refinitiv.dataplatform.content.ipa.enum_types import PriceSide

        return self._get_enum_parameter(PriceSide, "optionPriceSide")

    @option_price_side.setter
    def option_price_side(self, value):
        from refinitiv.dataplatform.content.ipa.enum_types import PriceSide

        self._set_enum_parameter(PriceSide, "optionPriceSide", value)

    @property
    def option_time_stamp(self):
        """
        :return: float
        """
        from refinitiv.dataplatform.content.ipa.enum_types import TimeStamp

        return self._get_enum_parameter(TimeStamp, "optionTimeStamp")

    @option_time_stamp.setter
    def option_time_stamp(self, value):
        from refinitiv.dataplatform.content.ipa.enum_types import TimeStamp

        self._set_enum_parameter(TimeStamp, "optionTimeStamp", value)

    @property
    def price_side(self):
        """
        :return: float
        """
        from refinitiv.dataplatform.content.ipa.enum_types import PriceSide

        return self._get_enum_parameter(PriceSide, "priceSide")

    @price_side.setter
    def price_side(self, value):
        from refinitiv.dataplatform.content.ipa.enum_types import PriceSide

        self._set_enum_parameter(PriceSide, "priceSide", value)

    @property
    def pricing_model_type(self):
        """
        :return: float
        """
        from refinitiv.dataplatform.content.ipa.enum_types import PricingModelType

        return self._get_enum_parameter(PricingModelType, "pricingModelType")

    @pricing_model_type.setter
    def pricing_model_type(self, value):
        from refinitiv.dataplatform.content.ipa.enum_types import PricingModelType

        self._set_enum_parameter(PricingModelType, "pricingModelType", value)

    @property
    def risk_free_rate_percent(self):
        """
        :return: float
        """
        return self._get_parameter("riskFreeRatePercent")

    @risk_free_rate_percent.setter
    def risk_free_rate_percent(self, value):
        self._set_parameter("riskFreeRatePercent", value)

    @property
    def risk_reversal_10d_object(self):
        """
        :return: BidAskMid
        """
        from refinitiv.dataplatform.content.ipa.models import BidAskMid

        return self._get_object_parameter(BidAskMid, "riskReversal10DObject")

    @risk_reversal_10d_object.setter
    def risk_reversal_10d_object(self, value):
        from refinitiv.dataplatform.content.ipa.models import BidAskMid

        self._set_object_parameter(BidAskMid, "riskReversal10DObject", value)

    @property
    def risk_reversal_25d_object(self):
        """
        :return: BidAskMid
        """
        from refinitiv.dataplatform.content.ipa.models import BidAskMid

        return self._get_object_parameter(BidAskMid, "riskReversal25DObject")

    @risk_reversal_25d_object.setter
    def risk_reversal_25d_object(self, value):
        from refinitiv.dataplatform.content.ipa.models import BidAskMid

        self._set_object_parameter(BidAskMid, "riskReversal25DObject", value)

    @property
    def underlying_price(self):
        """
        :return: float
        """
        return self._get_parameter("underlyingPrice")

    @underlying_price.setter
    def underlying_price(self, value):
        self._set_parameter("underlyingPrice", value)

    @property
    def underlying_price_side(self):
        """
        :return: enum PriceSide
        """
        from refinitiv.dataplatform.content.ipa.enum_types import PriceSide

        return self._get_enum_parameter(PriceSide, "underlyingPriceSide")

    @underlying_price_side.setter
    def underlying_price_side(self, value):
        from refinitiv.dataplatform.content.ipa.enum_types import PriceSide

        self._set_enum_parameter(PriceSide, "underlyingPriceSide", value)

    @property
    def underlying_time_stamp(self):
        """
        :return: enum TimeStamp
        """
        from refinitiv.dataplatform.content.ipa.enum_types import TimeStamp

        return self._get_enum_parameter(TimeStamp, "underlyingTimeStamp")

    @underlying_time_stamp.setter
    def underlying_time_stamp(self, value):
        from refinitiv.dataplatform.content.ipa.enum_types import TimeStamp

        self._set_enum_parameter(TimeStamp, "underlyingTimeStamp", value)

    @property
    def valuation_date(self):
        """
        :return: string datetime
        """
        return self._get_parameter("valuationDate")

    @valuation_date.setter
    def valuation_date(self, value):
        self._set_parameter("valuationDate", value)

    @property
    def volatility_model(self):
        """
        :return: VolatilityModel
        """
        from refinitiv.dataplatform.content.ipa.enum_types import VolatilityModel

        return self._get_enum_parameter(VolatilityModel, "volatilityModel")

    @volatility_model.setter
    def volatility_model(self, value):
        from refinitiv.dataplatform.content.ipa.enum_types import VolatilityModel

        self._set_enum_parameter(VolatilityModel, "volatilityModel", value)

    @property
    def volatility_percent(self):
        """
        :return: float
        """
        return self._get_parameter("volatilityPercent")

    @volatility_percent.setter
    def volatility_percent(self, value):
        self._set_parameter("volatilityPercent", value)

    @property
    def volatility_type(self):
        """
        :return: string
        """
        from refinitiv.dataplatform.content.ipa.enum_types import VolatilityType

        return self._get_enum_parameter(VolatilityType, "volatilityType")

    @volatility_type.setter
    def volatility_type(self, value):
        from refinitiv.dataplatform.content.ipa.enum_types import VolatilityType

        self._set_enum_parameter(VolatilityType, "volatilityType", value)

    @property
    def market_data_date(self):
        """
        :return: str
        """
        return self._get_parameter("marketDataDate")

    @market_data_date.setter
    def market_data_date(self, value):
        self._set_parameter("marketDataDate", value)
