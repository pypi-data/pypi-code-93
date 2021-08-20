# coding: utf8
# contract_gen 2020-05-13 12:48:48.791016


__all__ = ["CalculationParams"]

from ...instrument import InstrumentCalculationParams


class CalculationParams(InstrumentCalculationParams):
    def __init__(
        self,
        *,
        valuation_date=None,
        market_data_date=None,
        report_ccy=None,
        upfront_amount_in_deal_ccy=None,
        upfront_percent=None,
        clean_price_percent=None,
        conventional_spread_bp=None,
        cash_amount_in_deal_ccy=None,
    ):
        super().__init__()
        self.valuation_date = valuation_date
        self.market_data_date = market_data_date
        self.report_ccy = report_ccy
        self.upfront_amount_in_deal_ccy = upfront_amount_in_deal_ccy
        self.upfront_percent = upfront_percent
        self.clean_price_percent = clean_price_percent
        self.conventional_spread_bp = conventional_spread_bp
        self.cash_amount_in_deal_ccy = cash_amount_in_deal_ccy

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
    def report_ccy(self):
        """
        :return: str
        """
        return self._get_parameter("reportCcy")

    @report_ccy.setter
    def report_ccy(self, value):
        self._set_parameter("reportCcy", value)

    @property
    def cash_amount_in_deal_ccy(self):
        """
        CashAmountInDealCcy to override and that will be used as pricing analysis input to compute the cds other outputs.
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("cashAmountInDealCcy")

    @cash_amount_in_deal_ccy.setter
    def cash_amount_in_deal_ccy(self, value):
        self._set_parameter("cashAmountInDealCcy", value)

    @property
    def clean_price_percent(self):
        """
        CleanPricePercent to override and that will be used as pricing analysis input to compute the cds other outputs.
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("cleanPricePercent")

    @clean_price_percent.setter
    def clean_price_percent(self, value):
        self._set_parameter("cleanPricePercent", value)

    @property
    def conventional_spread_bp(self):
        """
        ConventionalSpreadBp to override and that will be used as pricing analysis input to compute the cds other outputs.
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("conventionalSpreadBp")

    @conventional_spread_bp.setter
    def conventional_spread_bp(self, value):
        self._set_parameter("conventionalSpreadBp", value)

    @property
    def upfront_amount_in_deal_ccy(self):
        """
        UpfrontAmountInDealCcy to override and that will be used as pricing analysis input to compute the cds other outputs.
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("upfrontAmountInDealCcy")

    @upfront_amount_in_deal_ccy.setter
    def upfront_amount_in_deal_ccy(self, value):
        self._set_parameter("upfrontAmountInDealCcy", value)

    @property
    def upfront_percent(self):
        """
        UpfrontPercent to override and that will be used as pricing analysis input to compute the cds other outputs.
        Optional. No override is applied by default. Note that only one pricing analysis input should be defined.
        :return: float
        """
        return self._get_parameter("upfrontPercent")

    @upfront_percent.setter
    def upfront_percent(self, value):
        self._set_parameter("upfrontPercent", value)

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
