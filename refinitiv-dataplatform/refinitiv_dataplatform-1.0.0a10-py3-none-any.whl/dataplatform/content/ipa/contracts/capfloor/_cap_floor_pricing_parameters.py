# coding: utf8
# contract_gen 2020-06-03 11:34:39.494947


__all__ = ["CalculationParams"]

from ...instrument import InstrumentCalculationParams
from ...enum_types.index_convexity_adjustment_integration_method import (
    IndexConvexityAdjustmentIntegrationMethod,
)
from ...enum_types.index_convexity_adjustment_method import (
    IndexConvexityAdjustmentMethod,
)


class CalculationParams(InstrumentCalculationParams):
    def __init__(
        self,
        index_convexity_adjustment_integration_method=None,
        index_convexity_adjustment_method=None,
        market_value_in_deal_ccy=None,
        report_ccy=None,
        skip_first_cap_floorlet=None,
        valuation_date=None,
    ):
        super().__init__()
        self.index_convexity_adjustment_integration_method = (
            index_convexity_adjustment_integration_method
        )
        self.index_convexity_adjustment_method = index_convexity_adjustment_method
        self.market_value_in_deal_ccy = market_value_in_deal_ccy
        self.report_ccy = report_ccy
        self.skip_first_cap_floorlet = skip_first_cap_floorlet
        self.valuation_date = valuation_date

    @property
    def index_convexity_adjustment_integration_method(self):
        """
        :return: enum IndexConvexityAdjustmentIntegrationMethod
        """
        return self._get_enum_parameter(
            IndexConvexityAdjustmentIntegrationMethod,
            "indexConvexityAdjustmentIntegrationMethod",
        )

    @index_convexity_adjustment_integration_method.setter
    def index_convexity_adjustment_integration_method(self, value):
        self._set_enum_parameter(
            IndexConvexityAdjustmentIntegrationMethod,
            "indexConvexityAdjustmentIntegrationMethod",
            value,
        )

    @property
    def index_convexity_adjustment_method(self):
        """
        :return: enum IndexConvexityAdjustmentMethod
        """
        return self._get_enum_parameter(
            IndexConvexityAdjustmentMethod, "indexConvexityAdjustmentMethod"
        )

    @index_convexity_adjustment_method.setter
    def index_convexity_adjustment_method(self, value):
        self._set_enum_parameter(
            IndexConvexityAdjustmentMethod, "indexConvexityAdjustmentMethod", value
        )

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
    def report_ccy(self):
        """
        Valuation is performed in deal currency. If a report currency is set, valuation is done in that report currency.
        :return: str
        """
        return self._get_parameter("reportCcy")

    @report_ccy.setter
    def report_ccy(self, value):
        self._set_parameter("reportCcy", value)

    @property
    def skip_first_cap_floorlet(self):
        """
        Indicates whether to take in consideration the first caplet
        :return: bool
        """
        return self._get_parameter("skipFirstCapFloorlet")

    @skip_first_cap_floorlet.setter
    def skip_first_cap_floorlet(self, value):
        self._set_parameter("skipFirstCapFloorlet", value)

    @property
    def valuation_date(self):
        """
        The valuation date for pricing.
        Optional. If not set the valuation date is equal to MarketDataDate or Today. For assets that contains a settlementConvention, the default valuation date  is equal to the settlementdate of the Asset that is usually the TradeDate+SettlementConvention.
        :return: str
        """
        return self._get_parameter("valuationDate")

    @valuation_date.setter
    def valuation_date(self, value):
        self._set_parameter("valuationDate", value)
