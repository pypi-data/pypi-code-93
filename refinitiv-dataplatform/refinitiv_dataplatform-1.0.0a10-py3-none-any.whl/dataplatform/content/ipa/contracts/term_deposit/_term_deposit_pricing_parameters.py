# coding: utf8
# contract_gen 2020-06-03 11:34:39.574948


__all__ = ["CalculationParams"]

from ...instrument import InstrumentCalculationParams
from ...enum_types.price_side import PriceSide


class CalculationParams(InstrumentCalculationParams):
    def __init__(self, price_side=None, income_tax_percent=None, valuation_date=None):
        super().__init__()
        self.price_side = price_side
        self.income_tax_percent = income_tax_percent
        self.valuation_date = valuation_date

    @property
    def price_side(self):
        """
        Price Side to consider when retrieving Market Data
        :return: enum PriceSide
        """
        return self._get_enum_parameter(PriceSide, "priceSide")

    @price_side.setter
    def price_side(self, value):
        self._set_enum_parameter(PriceSide, "priceSide", value)

    @property
    def income_tax_percent(self):
        """
        Income tax percent is substracted from applied interest rate percents in the end of deposit.
        Example "5" means 5%
        :return: float
        """
        return self._get_parameter("incomeTaxPercent")

    @income_tax_percent.setter
    def income_tax_percent(self, value):
        self._set_parameter("incomeTaxPercent", value)

    @property
    def valuation_date(self):
        """
        The valuation date for pricing.
        Optional. If not set the valuation date is equal to MarketDataDate or Today. For assets that contains a settlementConvention,
        the default valuation date  is equal to the settlementdate of the Asset that is usually the TradeDate+SettlementConvention.
        :return: str
        """
        return self._get_parameter("valuationDate")

    @valuation_date.setter
    def valuation_date(self, value):
        self._set_parameter("valuationDate", value)
