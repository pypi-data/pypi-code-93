# coding: utf8
# contract_gen 2020-05-13 12:48:48.788016

__all__ = ["PremiumLegDefinition"]

from ...instrument._definition import ObjectDefinition
from ...enum_types.stub_rule import StubRule
from ...enum_types.direction import Direction
from ...enum_types.frequency import Frequency
from ...enum_types.day_count_basis import DayCountBasis
from ...enum_types.business_day_convention import BusinessDayConvention


class PremiumLegDefinition(ObjectDefinition):
    def __init__(
        self,
        *,
        direction,
        notional_ccy=None,
        notional_amount=None,
        fixed_rate_percent=None,
        interest_payment_ccy,
        interest_payment_frequency,
        interest_calculation_method,
        accrued_calculation_method=None,
        payment_business_day_convention=None,
        first_regular_payment_date=None,
        last_regular_payment_date=None,
        payment_business_days=None,
        stub_rule=None,
        accrued_paid_on_default=None,
    ):
        super().__init__()
        self.direction = direction
        self.notional_ccy = notional_ccy
        self.notional_amount = notional_amount
        self.fixed_rate_percent = fixed_rate_percent
        self.interest_payment_frequency = interest_payment_frequency
        self.interest_calculation_method = interest_calculation_method
        self.accrued_calculation_method = accrued_calculation_method
        self.payment_business_day_convention = payment_business_day_convention
        self.first_regular_payment_date = first_regular_payment_date
        self.last_regular_payment_date = last_regular_payment_date
        self.payment_business_days = payment_business_days
        self.stub_rule = stub_rule
        self.accrued_paid_on_default = accrued_paid_on_default
        self.interest_payment_ccy = interest_payment_ccy

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
    def accrued_paid_on_default(self):
        """
        Specifies whether the accrued is paid at the credit event date or not.
        - true :  the accrued is paid at the credit event date
        - false :  the accrued is not paid at the credit event date
        Optional. Defaults to false.
        :return: bool
        """
        return self._get_parameter("accruedPaidOnDefault")

    @accrued_paid_on_default.setter
    def accrued_paid_on_default(self, value):
        self._set_parameter("accruedPaidOnDefault", value)

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
    def interest_payment_ccy(self):
        """
        The ISO code of the interest payment currency.
        Mandatory.
        :return: str
        """
        return self._get_parameter("interestPaymentCcy")

    @interest_payment_ccy.setter
    def interest_payment_ccy(self, value):
        self._set_parameter("interestPaymentCcy", value)

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
