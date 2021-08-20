# coding: utf8
# contract_gen 2020-06-03 11:34:39.492922

__all__ = ["Definition"]

from ...instrument.instrument_definition import InstrumentDefinition
from ...enum_types.stub_rule import StubRule
from ...enum_types.buy_sell import BuySell
from ...enum_types.adjust_interest_to_payment_date import AdjustInterestToPaymentDate
from ...enum_types.day_count_basis import DayCountBasis
from ...enum_types.business_day_convention import BusinessDayConvention
from ...enum_types.date_rolling_convention import DateRollingConvention
from ...enum_types.frequency import Frequency
from ...enum_types.index_reset_type import IndexResetType
from ...models import AmortizationItem


class Definition(InstrumentDefinition):
    def __init__(
        self,
        *,
        instrument_tag=None,
        start_date=None,
        end_date=None,
        tenor=None,
        notional_ccy,
        notional_amount=None,
        index_name=None,
        index_tenor=None,
        interest_payment_frequency=None,
        interest_calculation_method=None,
        payment_business_day_convention=None,
        payment_roll_convention=None,
        index_reset_frequency=None,
        index_reset_type=None,
        index_fixing_lag=None,
        amortization_schedule=None,
        adjust_interest_to_payment_date=None,
        buy_sell,
        cap_strike_percent,
        floor_strike_percent=None,
        index_fixing_ric=None,
        stub_rule=None,
    ):
        super().__init__()
        self.instrument_tag = instrument_tag
        self.start_date = start_date
        self.end_date = end_date
        self.tenor = tenor
        self.notional_ccy = notional_ccy
        self.notional_amount = notional_amount
        self.index_name = index_name
        self.index_tenor = index_tenor
        self.interest_payment_frequency = interest_payment_frequency
        self.interest_calculation_method = interest_calculation_method
        self.payment_business_day_convention = payment_business_day_convention
        self.payment_roll_convention = payment_roll_convention
        self.index_reset_frequency = index_reset_frequency
        self.index_reset_type = index_reset_type
        self.index_fixing_lag = index_fixing_lag
        self.amortization_schedule = amortization_schedule
        self.adjust_interest_to_payment_date = adjust_interest_to_payment_date
        self.buy_sell = buy_sell
        self.cap_strike_percent = cap_strike_percent
        self.floor_strike_percent = floor_strike_percent
        self.index_fixing_ric = index_fixing_ric
        self.stub_rule = stub_rule

    @classmethod
    def get_instrument_type(cls):
        return "CapFloor"

    @property
    def adjust_interest_to_payment_date(self):
        """
        A flag that indicates if the coupon dates are adjusted to the payment dates.
        Optional. By default 'false' is used.
        :return: enum AdjustInterestToPaymentDate
        """
        return self._get_enum_parameter(
            AdjustInterestToPaymentDate, "adjustInterestToPaymentDate"
        )

    @adjust_interest_to_payment_date.setter
    def adjust_interest_to_payment_date(self, value):
        self._set_enum_parameter(
            AdjustInterestToPaymentDate, "adjustInterestToPaymentDate", value
        )

    @property
    def amortization_schedule(self):
        """
        Definition of amortizations
        :return: list AmortizationItem
        """
        return self._get_list_parameter(AmortizationItem, "amortizationSchedule")

    @amortization_schedule.setter
    def amortization_schedule(self, value):
        self._set_list_parameter(AmortizationItem, "amortizationSchedule", value)

    @property
    def buy_sell(self):
        """
        The side of the deal. Possible values:
         - Buy
         - Sell
        :return: enum BuySell
        """
        return self._get_enum_parameter(BuySell, "buySell")

    @buy_sell.setter
    def buy_sell(self, value):
        self._set_enum_parameter(BuySell, "buySell", value)

    @property
    def index_reset_frequency(self):
        """
        The reset frequency in case the leg Type is Float.
        Optional. By default the IndexTenor is used.
        :return: enum Frequency
        """
        return self._get_enum_parameter(Frequency, "indexResetFrequency")

    @index_reset_frequency.setter
    def index_reset_frequency(self, value):
        self._set_enum_parameter(Frequency, "indexResetFrequency", value)

    @property
    def index_reset_type(self):
        """
        A flag that indicates if the floating rate index is reset before the coupon period starts or at the end of the coupon period.
        The possible values are:
         - InAdvance (resets the index before the start of the interest period),
         - InArrears (resets the index at the end of the interest period).
        Optional. By default 'InAdvance' is used.
        :return: enum IndexResetType
        """
        return self._get_enum_parameter(IndexResetType, "indexResetType")

    @index_reset_type.setter
    def index_reset_type(self, value):
        self._set_enum_parameter(IndexResetType, "indexResetType", value)

    @property
    def interest_calculation_method(self):
        """
        The Day Count Basis method used to calculate the coupon interest payments.
        Mandatory.
        :return: enum DayCountBasis
        """
        return self._get_enum_parameter(DayCountBasis, "interestCalculationMethod")

    @interest_calculation_method.setter
    def interest_calculation_method(self, value):
        self._set_enum_parameter(DayCountBasis, "interestCalculationMethod", value)

    @property
    def interest_payment_frequency(self):
        """
        The frequency of the interest payments.
        Optional if an instrument code/style have been defined : in that case, value comes from reference data. Otherwise, it is mandatory.
        :return: enum Frequency
        """
        return self._get_enum_parameter(Frequency, "interestPaymentFrequency")

    @interest_payment_frequency.setter
    def interest_payment_frequency(self, value):
        self._set_enum_parameter(Frequency, "interestPaymentFrequency", value)

    @property
    def payment_business_day_convention(self):
        """
        The method to adjust dates to a working day.
        The possible values are:
         - ModifiedFollowing (adjusts dates according to the Modified Following convention - next business day unless is it
            goes into the next month, preceeding is used in that  case),
         - NextBusinessDay (adjusts dates according to the Following convention - Next Business Day),
         - PreviousBusinessDay (adjusts dates  according to the Preceeding convention - Previous Business Day),
         - NoMoving (does not adjust dates),
         - BbswModifiedFollowing (adjusts dates  according to the BBSW Modified Following convention).
        Optional. In case an instrument code/style has been defined, value comes from bond reference data. Otherwise 'ModifiedFollowing' is used.
        :return: enum BusinessDayConvention
        """
        return self._get_enum_parameter(
            BusinessDayConvention, "paymentBusinessDayConvention"
        )

    @payment_business_day_convention.setter
    def payment_business_day_convention(self, value):
        self._set_enum_parameter(
            BusinessDayConvention, "paymentBusinessDayConvention", value
        )

    @property
    def payment_roll_convention(self):
        """
        The method to adjust payment dates whn they fall at the end of the month (28th of February, 30th, 31st).
        The possible values are:
         - Last (For setting the calculated date to the last working day),
         - Same (For setting the calculated date to the same day . In this latter case, the date may be moved according to the date
            moving convention if it is a non-working day),
         - Last28 (For setting the calculated date to the last working day. 28FEB being always considered as the last working day),
         - Same28 (For setting the calculated date to the same day .28FEB being always considered as the last working day).
        Optional. By default 'SameDay' is used.
        :return: enum DateRollingConvention
        """
        return self._get_enum_parameter(DateRollingConvention, "paymentRollConvention")

    @payment_roll_convention.setter
    def payment_roll_convention(self, value):
        self._set_enum_parameter(DateRollingConvention, "paymentRollConvention", value)

    @property
    def cap_strike_percent(self):
        """
        Cap leg strike expressed in %
        :return: float
        """
        return self._get_parameter("capStrikePercent")

    @cap_strike_percent.setter
    def cap_strike_percent(self, value):
        self._set_parameter("capStrikePercent", value)

    @property
    def end_date(self):
        """
        The maturity date of the CapFloor
        :return: str
        """
        return self._get_parameter("endDate")

    @end_date.setter
    def end_date(self, value):
        self._set_parameter("endDate", value)

    @property
    def floor_strike_percent(self):
        """
        Floor leg strike expressed in %
        :return: float
        """
        return self._get_parameter("floorStrikePercent")

    @floor_strike_percent.setter
    def floor_strike_percent(self, value):
        self._set_parameter("floorStrikePercent", value)

    @property
    def index_fixing_lag(self):
        """
        Defines the number of working days between the fixing date and the start of the coupon period ('InAdvance') or
        the end of the coupon period ('InArrears').
        Optional. By default 0 is used.
        :return: int
        """
        return self._get_parameter("indexFixingLag")

    @index_fixing_lag.setter
    def index_fixing_lag(self, value):
        self._set_parameter("indexFixingLag", value)

    @property
    def index_fixing_ric(self):
        """
        The RIC that carries the fixing value. This value overrides the RIC associated by default with the IndexName and IndexTenor.
        Optional.
        :return: str
        """
        return self._get_parameter("indexFixingRic")

    @index_fixing_ric.setter
    def index_fixing_ric(self, value):
        self._set_parameter("indexFixingRic", value)

    @property
    def index_name(self):
        """
        The name of the floating rate index.
        :return: str
        """
        return self._get_parameter("indexName")

    @index_name.setter
    def index_name(self, value):
        self._set_parameter("indexName", value)

    @property
    def index_tenor(self):
        """
        The period code that represents the maturity of the floating rate index.
        Mandatory when the leg is float.
        :return: str
        """
        return self._get_parameter("indexTenor")

    @index_tenor.setter
    def index_tenor(self, value):
        self._set_parameter("indexTenor", value)

    @property
    def instrument_tag(self):
        """
        User defined string to identify the instrument.It can be used to link output results to the instrument definition.
        Only alphabetic, numeric and '- _.#=@' characters are supported.
        Optional.
        :return: str
        """
        return self._get_parameter("instrumentTag")

    @instrument_tag.setter
    def instrument_tag(self, value):
        self._set_parameter("instrumentTag", value)

    @property
    def notional_amount(self):
        """
        The notional amount of the leg at the period start date.
        Optional. By default 1,000,000 is used.
        :return: float
        """
        return self._get_parameter("notionalAmount")

    @notional_amount.setter
    def notional_amount(self, value):
        self._set_parameter("notionalAmount", value)

    @property
    def notional_ccy(self):
        """
        The ISO code of the notional currency.
        Mandatory if instrument code or instrument style has not been defined.
        In case an instrument code/style has been defined, value may comes from the reference data.
        :return: str
        """
        return self._get_parameter("notionalCcy")

    @notional_ccy.setter
    def notional_ccy(self, value):
        self._set_parameter("notionalCcy", value)

    @property
    def start_date(self):
        """
        The option start date
        :return: str
        """
        return self._get_parameter("startDate")

    @start_date.setter
    def start_date(self, value):
        self._set_parameter("startDate", value)

    @property
    def tenor(self):
        """
        Tenor of the option
        :return: str
        """
        return self._get_parameter("tenor")

    @tenor.setter
    def tenor(self, value):
        self._set_parameter("tenor", value)

    @property
    def stub_rule(self):
        """
        The rule that defines whether coupon roll dates are aligned on the  maturity or the issue date.
        The possible values are:
         - ShortFirstProRata (to create a short period between the start date and the first coupon date, and pay a smaller amount of interest for the short period.All coupon dates are calculated backward from the maturity date),
         - ShortFirstFull (to create a short period between the start date and the first coupon date, and pay a regular coupon on the first coupon date. All coupon dates are calculated backward from the maturity date),
         - LongFirstFull (to create a long period between the start date and the second coupon date, and pay a regular coupon on the second coupon date. All coupon dates are calculated backward from the maturity date),
         - ShortLastProRata (to create a short period between the last payment date and maturity, and pay a smaller amount of interest for the short period. All coupon dates are calculated forward from the start date).
        This property may also be used in conjunction with firstRegularPaymentDate and lastRegularPaymentDate; in that case the following values can be defined:
         - Issue (all dates are aligned on the issue date),
         - Maturity (all dates are aligned on the maturity date).
        Optional. By default 'Maturity' is used.
        :return: enum StubRule
        """
        return self._get_enum_parameter(StubRule, "stubRule")

    @stub_rule.setter
    def stub_rule(self, value):
        self._set_enum_parameter(StubRule, "stubRule", value)
