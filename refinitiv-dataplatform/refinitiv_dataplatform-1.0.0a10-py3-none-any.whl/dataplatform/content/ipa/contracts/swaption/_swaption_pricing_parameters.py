# coding: utf8
# contract_gen 2020-05-19 11:08:13.671204

__all__ = ["CalculationParams"]

from . import SwaptionMarketDataRule
from ...enum_types.discounting_type import DiscountingType
from ...instrument import InstrumentCalculationParams


class CalculationParams(InstrumentCalculationParams):
    def __init__(
        self,
        market_data_rule=None,
        market_value_in_deal_ccy=None,
        nb_iterations=None,
        valuation_date=None,
    ):
        super().__init__()
        self.market_data_rule = market_data_rule
        self.market_value_in_deal_ccy = market_value_in_deal_ccy
        self.nb_iterations = nb_iterations
        self.valuation_date = valuation_date

    @property
    def market_data_rule(self):
        """
        :return: object SwaptionMarketDataRule
        """
        return self._get_object_parameter(SwaptionMarketDataRule, "marketDataRule")

    @market_data_rule.setter
    def market_data_rule(self, value):
        self._set_object_parameter(SwaptionMarketDataRule, "marketDataRule", value)

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
    def nb_iterations(self):
        """
        Used for Bermudans and HW1F tree
        :return: int
        """
        return self._get_parameter("nbIterations")

    @nb_iterations.setter
    def nb_iterations(self, value):
        self._set_parameter("nbIterations", value)

    @property
    def valuation_date(self):
        """
        The valuation date for pricing.
        Optional. If not set the valuation date is equal to MarketDataDate or Today.
        For assets that contains a settlementConvention, the default valuation date  is equal to
        the settlementdate of the Asset that is usually the TradeDate+SettlementConvention.
        :return: str
        """
        return self._get_parameter("valuationDate")

    @valuation_date.setter
    def valuation_date(self, value):
        self._set_parameter("valuationDate", value)
