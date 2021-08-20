# coding: utf8
# contract_gen 2020-05-18 08:30:59.280857


__all__ = ["CalculationParams"]

from ...instrument import InstrumentCalculationParams
from ...enum_types.price_side import PriceSide
from ...enum_types.fx_swap_calculation_method import FxSwapCalculationMethod


class CalculationParams(InstrumentCalculationParams):
    def __init__(
        self,
        valuation_date=None,
        market_data_date=None,
        report_ccy=None,
        ignore_ref_ccy_holidays=None,
        fx_swap_calculation_method=None,
        price_side=None,
        calc_end_from_fwd_start=None,
        calc_end_from_pre_spot_start=None,
        # user_turn_dates=None,
        # ignore_usd_holidays=None,
        # one_day_values=None,
        # roll_over_time_policy=None,
        # spread_margin_in_bp=None,
        # turns_calibration=None,
    ):
        super().__init__()
        self.valuation_date = valuation_date
        self.market_data_date = market_data_date
        self.report_ccy = report_ccy
        self.ignore_ref_ccy_holidays = ignore_ref_ccy_holidays
        self.fx_swap_calculation_method = fx_swap_calculation_method
        self.price_side = price_side
        # self.fx_swaps_ccy1 = fx_swaps_ccy1
        # self.fx_swaps_ccy2 = fx_swaps_ccy2
        # self.deposit_ccy1 = deposit_ccy1
        # self.deposit_ccy2 = deposit_ccy2
        # self.calc_end_from_start = calc_end_from_start
        # self.user_turn_dates = user_turn_dates
        # self.ignore_usd_holidays = ignore_usd_holidays
        # self.one_day_values = one_day_values
        # self.roll_over_time_policy = roll_over_time_policy
        # self.spread_margin_in_bp = spread_margin_in_bp
        # self.turns_calibration = turns_calibration
        self.calc_end_from_fwd_start = calc_end_from_fwd_start
        self.calc_end_from_pre_spot_start = calc_end_from_pre_spot_start

    @property
    def report_ccy(self):
        return self._get_parameter("reportCcy")

    @report_ccy.setter
    def report_ccy(self, value):
        self._set_parameter("reportCcy", value)

    @property
    def market_data_date(self):
        """
        The market data date for pricing.
        Optional. By default, the marketDataDate date is the ValuationDate or Today.
        :return: datetime
        """
        return self._get_parameter("marketDataDate")

    @market_data_date.setter
    def market_data_date(self, value):
        self._set_parameter("marketDataDate", value)

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
    def price_side(self):
        """
        The type of price returned for pricing Analysis: Bid(Bid value), Ask(Ask value), Mid(Mid value)
        Optional. Defaults to 'Mid'.
        :return: enum PriceSide
        """
        return self._get_enum_parameter(PriceSide, "priceSide")

    @price_side.setter
    def price_side(self, value):
        self._set_enum_parameter(PriceSide, "priceSide", value)

    # @property
    # def user_turn_dates(self):
    #     """
    #     :return: list string
    #     """
    #     return self._get_list_parameter(str, "userTurnDates")
    #
    # @user_turn_dates.setter
    # def user_turn_dates(self, value):
    #     self._set_list_parameter(str, "userTurnDates", value)

    @property
    def ignore_ref_ccy_holidays(self):
        """
        The reference currency holidays flag : When dates are computed, its possible to choose if holidays of the reference currency are included or not in the pricing
        Optional. Defaults to 'false'.
        :return: bool
        """
        return self._get_parameter("ignoreRefCcyHolidays")

    @ignore_ref_ccy_holidays.setter
    def ignore_ref_ccy_holidays(self, value):
        self._set_parameter("ignoreRefCcyHolidays", value)

    # @property
    # def ignore_usd_holidays(self):
    #     """
    #     :return: bool
    #     """
    #     return self._get_parameter("ignoreUSDHolidays")
    #
    # @ignore_usd_holidays.setter
    # def ignore_usd_holidays(self, value):
    #     self._set_parameter("ignoreUSDHolidays", value)

    # @property
    # def one_day_values(self):
    #     """
    #     :return: str
    #     """
    #     return self._get_parameter("oneDayValues")
    #
    # @one_day_values.setter
    # def one_day_values(self, value):
    #     self._set_parameter("oneDayValues", value)

    # @property
    # def roll_over_time_policy(self):
    #     """
    #     :return: str
    #     """
    #     return self._get_parameter("rollOverTimePolicy")
    #
    # @roll_over_time_policy.setter
    # def roll_over_time_policy(self, value):
    #     self._set_parameter("rollOverTimePolicy", value)

    # @property
    # def spread_margin_in_bp(self):
    #     """
    #     If activated, it will calculate the indicated points in market data section instead of taking them directly from the curves
    #     :return: float
    #     """
    #     return self._get_parameter("spreadMarginInBp")
    #
    # @spread_margin_in_bp.setter
    # def spread_margin_in_bp(self, value):
    #     self._set_parameter("spreadMarginInBp", value)

    # @property
    # def turns_calibration(self):
    #     """
    #     :return: str
    #     """
    #     return self._get_parameter("turnsCalibration")
    #
    # @turns_calibration.setter
    # def turns_calibration(self, value):
    #     self._set_parameter("turnsCalibration", value)

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
    def calc_end_from_fwd_start(self):
        """
        :return: bool
        """
        return self._get_parameter("calcEndFromFwdStart")

    @calc_end_from_fwd_start.setter
    def calc_end_from_fwd_start(self, value):
        self._set_parameter("calcEndFromFwdStart", value)

    @property
    def calc_end_from_pre_spot_start(self):
        """
        :return: bool
        """
        return self._get_parameter("calcEndFromPreSpotStart")

    @calc_end_from_pre_spot_start.setter
    def calc_end_from_pre_spot_start(self, value):
        self._set_parameter("calcEndFromPreSpotStart", value)
