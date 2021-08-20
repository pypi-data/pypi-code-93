# coding: utf8
# contract_gen 2020-05-19 11:08:13.655204


__all__ = ["CalculationParams"]

from ...instrument import InstrumentCalculationParams
from ...enum_types.repo_curve_type import RepoCurveType


class CalculationParams(InstrumentCalculationParams):
    def __init__(
        self,
        valuation_date=None,
        market_data_date=None,
        settlement_convention=None,
        report_ccy=None,
        coupon_reinvestment_rate_percent=None,
        repo_curve_type=None,
    ):
        super().__init__()
        self.valuation_date = valuation_date
        self.market_data_date = market_data_date
        self.settlement_convention = settlement_convention
        self.report_ccy = report_ccy
        self.coupon_reinvestment_rate_percent = coupon_reinvestment_rate_percent
        self.repo_curve_type = repo_curve_type

    @property
    def coupon_reinvestment_rate_percent(self):
        """
        Rate used to reinvest the underlying asset's income.
        By default 0.
        :return: str
        """
        return self._get_parameter("couponReinvestmentRatePercent")

    @coupon_reinvestment_rate_percent.setter
    def coupon_reinvestment_rate_percent(self, value):
        self._set_parameter("couponReinvestmentRatePercent", value)

    @property
    def settlement_convention(self):
        """
        Settlement tenor for the repo. By default, the rule is that  repoStartDate = valuationDate = marketDataDate + settlementConvention.
        By default, the settlement convention is equal to the settlement convention of the underlying asset.
        :return: str
        """
        return self._get_parameter("settlementConvention")

    @settlement_convention.setter
    def settlement_convention(self, value):
        self._set_parameter("settlementConvention", value)

    @property
    def report_ccy(self):
        """
        Pricing data is computed in deal currency. If a report currency is set, pricing data is also computed in report currency.
        By default, Bond notional currency.
        :return: str
        """
        return self._get_parameter("reportCcy")

    @report_ccy.setter
    def report_ccy(self, value):
        self._set_parameter("reportCcy", value)

    @property
    def market_data_date(self):
        """
        The valuation date for pricing. The valuation date is the date where cash flow is discounted.
        By default, valuationDate is computed from marketDataDate and settlement convention.
        :return: datetime
        """
        return self._get_parameter("marketDataDate")

    @market_data_date.setter
    def market_data_date(self, value):
        self._set_parameter("marketDataDate", value)

    @property
    def repo_curve_type(self):
        """
        Curve used to compute the repo rate. it can be computed using following methods:

           - RepoCurve : rate is computed by interpolating a repo curve.

           - DepositCurve : rate is computed by interpolating a deposit curve.

           - FixingLibor : rate is computed by interpolating libor rates.

        If no curve can be found, the rate is computed using a deposit curve.
        :return: enum RepoCurveType
        """
        return self._get_enum_parameter(RepoCurveType, "repoCurveType")

    @repo_curve_type.setter
    def repo_curve_type(self, value):
        self._set_enum_parameter(RepoCurveType, "repoCurveType", value)

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
