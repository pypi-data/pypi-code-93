# coding: utf8


__all__ = ["LegDefinition"]

from refinitiv.dataplatform import RequiredError
from refinitiv.dataplatform.tools._common import is_any_defined
from ...enum_types.adjust_interest_to_payment_date import AdjustInterestToPaymentDate
from ...enum_types.day_count_basis import DayCountBasis
from ...enum_types.common_tools import is_enum_equal
from ...enum_types.business_day_convention import BusinessDayConvention
from ...enum_types.direction import Direction
from ...enum_types.frequency import Frequency
from ...enum_types.index_compounding_method import IndexCompoundingMethod
from ...enum_types.index_reset_type import IndexResetType
from ...enum_types.interest_type import InterestType
from ...enum_types.notional_exchange import NotionalExchange
from ...enum_types.date_rolling_convention import DateRollingConvention
from ...enum_types.stub_rule import StubRule
from ...instrument._definition import ObjectDefinition
from ...models import AmortizationItem


class LegDefinition(ObjectDefinition):
    def __init__(
        self,
        *,
        leg_tag=None,
        direction,
        interest_type,
        notional_ccy,
        notional_amount=None,
        fixed_rate_percent=None,
        index_name=None,
        index_tenor=None,
        index_fixing_ric=None,
        spread_bp=None,
        interest_payment_frequency,
        interest_calculation_method,
        accrued_calculation_method=None,
        payment_business_day_convention=None,
        payment_roll_convention=None,
        index_reset_frequency=None,
        index_reset_type=None,
        index_fixing_lag=None,
        first_regular_payment_date=None,
        last_regular_payment_date=None,
        amortization_schedule=None,
        payment_business_days=None,
        notional_exchange=None,
        adjust_interest_to_payment_date=None,
        index_compounding_method=None,
        interest_payment_delay=None,
        stub_rule=None,
    ):
        super().__init__()

        error = []
        if is_enum_equal(InterestType.FLOAT, interest_type):
            error.append("index_name required, if the leg is float.")
            is_any_defined(index_name) and error.pop()

        if error:
            raise RequiredError(-1, error)

        self.leg_tag = leg_tag
        self.direction = direction
        self.interest_type = interest_type
        self.notional_ccy = notional_ccy
        self.notional_amount = notional_amount
        self.fixed_rate_percent = fixed_rate_percent
        self.index_name = index_name
        self.index_tenor = index_tenor
        self.spread_bp = spread_bp
        self.interest_payment_frequency = interest_payment_frequency
        self.interest_calculation_method = interest_calculation_method
        self.accrued_calculation_method = accrued_calculation_method
        self.payment_business_day_convention = payment_business_day_convention
        self.payment_roll_convention = payment_roll_convention
        self.index_reset_frequency = index_reset_frequency
        self.index_reset_type = index_reset_type
        self.index_fixing_lag = index_fixing_lag
        self.first_regular_payment_date = first_regular_payment_date
        self.last_regular_payment_date = last_regular_payment_date
        self.amortization_schedule = amortization_schedule
        self.payment_business_days = payment_business_days
        self.notional_exchange = notional_exchange
        self.adjust_interest_to_payment_date = adjust_interest_to_payment_date
        self.index_compounding_method = index_compounding_method
        self.interest_payment_delay = interest_payment_delay
        self.stub_rule = stub_rule
        self.index_fixing_ric = index_fixing_ric
        # self.fixed_rate_percent_schedule = fixed_rate_percent_schedule

    @property
    def accrued_calculation_method(self):
        """
        The Day Count Basis method used to calculate the accrued interest payments.
        Optional. By default, the same value than InterestCalculationMethod is used.
        :return: enum DayCountBasis
        """
        return self._get_enum_parameter(DayCountBasis, "accruedCalculationMethod")

    @accrued_calculation_method.setter
    def accrued_calculation_method(self, value):
        self._set_enum_parameter(DayCountBasis, "accruedCalculationMethod", value)

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
    def direction(self):
        """
        The direction of the leg. the possible values are:

         'Paid' (the cash flows of the leg are paid to the counterparty),

         'Received' (the cash flows of the leg are received from the counterparty).

        Optional for a single leg instrument (like a bond), in that case default value is Received. It is mandatory for a multi-instrument leg instrument (like Swap or CDS leg).
        :return: enum Direction
        """
        return self._get_enum_parameter(Direction, "direction")

    @direction.setter
    def direction(self, value):
        self._set_enum_parameter(Direction, "direction", value)

    @property
    def index_compounding_method(self):
        """
        A flag that defines how the coupon rate is calculated from the reset floating rates when the reset frequency is higher than the interest payment frequency (e.g. daily index reset with quarterly interest payment).
        The possible values are:
         - Compounded (uses the compounded average rate from multiple fixings),
         - Average (uses the arithmetic average rate from multiple fixings),
         - Constant (uses the last published rate among multiple fixings),
         - AdjustedCompounded (uses Chinese 7-day repo fixing),
         - MexicanCompounded (uses Mexican Bremse fixing).
        Optional. By default 'Constant' is used.
        :return: enum IndexCompoundingMethod
        """
        return self._get_enum_parameter(
            IndexCompoundingMethod, "indexCompoundingMethod"
        )

    @index_compounding_method.setter
    def index_compounding_method(self, value):
        self._set_enum_parameter(
            IndexCompoundingMethod, "indexCompoundingMethod", value
        )

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
    def interest_type(self):
        """
        A flag that indicates whether the leg is fixed or float. Possible values are:
        - 'Fixed' (the leg has a fixed coupon),
        - 'Float' (the leg has a floating rate index).
        Mandatory.
        :return: enum InterestType
        """
        return self._get_enum_parameter(InterestType, "interestType")

    @interest_type.setter
    def interest_type(self, value):
        self._set_enum_parameter(InterestType, "interestType", value)

    @property
    def notional_exchange(self):
        """
        A flag that defines whether and when notional payments occurs.
        The possible values are:

         - None (means that the notional is not included in the cash flow schedule),

         - Start (means that the counterparties exchange the notional on the swap start date, before the first interest payment),

         - End (means that the counterparties exchange the notional on the swap maturity date, in addition to the last interest payment),

         - Both (combines the payments of Start Only and End Only),

         - EndAdjustment.
        :return: enum NotionalExchange
        """
        return self._get_enum_parameter(NotionalExchange, "notionalExchange")

    @notional_exchange.setter
    def notional_exchange(self, value):
        self._set_enum_parameter(NotionalExchange, "notionalExchange", value)

    @property
    def payment_business_day_convention(self):
        """
        The method to adjust dates to a working day.
        The possible values are:
         - ModifiedFollowing (adjusts dates according to the Modified Following convention - next business day unless is it goes into the next month, preceeding is used in that  case),
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

         - Same (For setting the calculated date to the same day . In this latter case, the date may be moved according to the date moving convention if it is a non-working day),

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

    @property
    def first_regular_payment_date(self):
        """
        The first regular coupon payment date for leg with an odd first coupon.
        Optional.
        :return: str
        """
        return self._get_parameter("firstRegularPaymentDate")

    @first_regular_payment_date.setter
    def first_regular_payment_date(self, value):
        self._set_parameter("firstRegularPaymentDate", value)

    @property
    def fixed_rate_percent(self):
        """
        The fixed coupon rate in percentage.
        It is mandatory in case of a single leg instrument. Otherwise, in case of multi leg instrument, it can be computed as the Par rate.
        :return: float
        """
        return self._get_parameter("fixedRatePercent")

    @fixed_rate_percent.setter
    def fixed_rate_percent(self, value):
        self._set_parameter("fixedRatePercent", value)

    @property
    def index_fixing_lag(self):
        """
        Defines the number of working days between the fixing date and the start of the coupon period ('InAdvance') or the end of the coupon period ('InArrears').
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
        Mandatory when the leg is float.
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
    def interest_payment_delay(self):
        """
        The number of working days between the end of coupon period and the actual interest payment date.
        Optional. By default no delay (0) is applied.
        :return: int
        """
        return self._get_parameter("interestPaymentDelay")

    @interest_payment_delay.setter
    def interest_payment_delay(self, value):
        self._set_parameter("interestPaymentDelay", value)

    @property
    def last_regular_payment_date(self):
        """
        The last regular coupon payment date for leg with an odd last coupon.
        Optional.
        :return: str
        """
        return self._get_parameter("lastRegularPaymentDate")

    @last_regular_payment_date.setter
    def last_regular_payment_date(self, value):
        self._set_parameter("lastRegularPaymentDate", value)

    @property
    def leg_tag(self):
        """
        A user provided string to identify the leg  that will also be part of the response.
        Optional.
        :return: str
        """
        return self._get_parameter("legTag")

    @leg_tag.setter
    def leg_tag(self, value):
        self._set_parameter("legTag", value)

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
        Mandatory if instrument code or instrument style has not been defined. In case an instrument code/style has been defined, value may comes from the reference data.
        :return: str
        """
        return self._get_parameter("notionalCcy")

    @notional_ccy.setter
    def notional_ccy(self, value):
        self._set_parameter("notionalCcy", value)

    @property
    def payment_business_days(self):
        """
        A list of coma-separated calendar codes to adjust dates (e.g. 'EMU' or 'USA').
        Optional. By default the calendar associated to NotionalCcy is used.
        :return: str
        """
        return self._get_parameter("paymentBusinessDays")

    @payment_business_days.setter
    def payment_business_days(self, value):
        self._set_parameter("paymentBusinessDays", value)

    @property
    def spread_bp(self):
        """
        The spread in basis point that is added to the floating rate index index value.
        Optional. By default 0 is used.
        :return: float
        """
        return self._get_parameter("spreadBp")

    @spread_bp.setter
    def spread_bp(self, value):
        self._set_parameter("spreadBp", value)
