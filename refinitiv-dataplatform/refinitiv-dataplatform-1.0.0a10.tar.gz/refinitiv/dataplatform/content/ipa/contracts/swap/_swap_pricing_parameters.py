# coding: utf8


__all__ = ["CalculationParams"]

from ...instrument import InstrumentCalculationParams
from ...enum_types.index_convexity_adjustment_method import (
    IndexConvexityAdjustmentMethod,
)
from ...enum_types.index_convexity_adjustment_integration_method import (
    IndexConvexityAdjustmentIntegrationMethod,
)


class CalculationParams(InstrumentCalculationParams):
    def __init__(
        self,
        valuation_date=None,
        report_ccy=None,
        market_data_date=None,
        index_convexity_adjustment_integration_method=None,
        index_convexity_adjustment_method=None,
        discounting_ccy=None,
        discounting_tenor=None,
        market_value_in_deal_ccy=None,
    ):
        super().__init__()
        self.valuation_date = valuation_date
        self.report_ccy = report_ccy
        self.market_data_date = market_data_date
        self.market_value_in_deal_ccy = market_value_in_deal_ccy
        self.index_convexity_adjustment_integration_method = (
            index_convexity_adjustment_integration_method
        )
        self.index_convexity_adjustment_method = index_convexity_adjustment_method
        self.discounting_ccy = discounting_ccy
        self.discounting_tenor = discounting_tenor

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

    @property
    def report_ccy(self):
        """
        :return: str
        """
        return self._get_parameter("reportCcy")

    @report_ccy.setter
    def report_ccy(self, value):
        self._set_parameter("reportCcy", value)

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
    def market_value_in_deal_ccy(self):
        """
        :return: float
        """
        return self._get_parameter("marketValueInDealCcy")

    @market_value_in_deal_ccy.setter
    def market_value_in_deal_ccy(self, value):
        self._set_parameter("marketValueInDealCcy", value)

    @property
    def discounting_tenor(self):
        """
        :return: str
        """
        return self._get_parameter("discountingTenor")

    @discounting_tenor.setter
    def discounting_tenor(self, value):
        self._set_parameter("discountingTenor", value)

    @property
    def discounting_ccy(self):
        """
        :return: str
        """
        return self._get_parameter("discountingCcy")

    @discounting_ccy.setter
    def discounting_ccy(self, value):
        self._set_parameter("discountingCcy", value)

    @property
    def index_convexity_adjustment_integration_method(self):
        """
        Integration method used for static replication method.
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
        Convexity adjustment type for CMS swaps and Libor in arrears swaps. Values can be: None, BlackScholes, LiborSwapMethod, or Replication
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
