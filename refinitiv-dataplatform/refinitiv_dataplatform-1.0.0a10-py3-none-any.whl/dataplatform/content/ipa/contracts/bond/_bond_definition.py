# coding: utf8


__all__ = ["Definition"]

from refinitiv.dataplatform.content.ipa.instrument.instrument_definition import (
    InstrumentDefinition,
)
from refinitiv.dataplatform.content.ipa.enum_types import Frequency
from refinitiv.dataplatform.content.ipa.enum_types import (
    DayCountBasis,
    BusinessDayConvention,
)
from refinitiv.dataplatform.content.ipa.enum_types import DateRollingConvention


class Definition(InstrumentDefinition):
    #
    # class Params(InstrumentDefinition.Params):
    #
    #     def __init__(self):
    #         super().__init__()
    #         # mandatory fields
    #         self._instrument_code = None
    #         self._issue_date = None
    #         self._end_date = None
    #         self._fixed_rate_percent = None
    #         self._interest_calculation_method = None
    #         self._notional_amount = None
    #         self._notional_ccy = None
    #         self._accrued_calculation_method = None
    #         self._payment_business_day_convention = None
    #         self._payment_roll_convention = DateRollingConvention.SAME
    #         self._interest_payment_frequency = None
    #
    #         # self._is_perpetual = None
    #         # # Optional fields from FixFloatInterestLegDefinition
    #         # self._interest_type = None
    #         # self._index_fixing_ric = None
    #         # self._spread_bp = 0
    #         # self._index_reset_frequency = None
    #         # self._index_fixing_lag = 0
    #         # self._interest_payment_delay = 0
    #         # self._index_compounded_method = IndexCompoundingMethod.CONSTANT
    #         # self._adjust_interest_to_payment_date = False
    #         # self._amortization_schedule = None
    #         # self._payment_business_days = None
    #         # self._stub_rule = StubRule.MATURITY
    #         # self._first_regular_payment_date = None
    #         # self._direction = Direction.RECEIVED
    #
    #     def with_instrument_code(self, value):
    #         """
    #         Code to define the bond instrument. It can be an ISIN, a RIC or an AssetId .
    #         """
    #         self._instrument_code = value
    #         return self
    #
    #     def with_issue_date(self, value):
    #         """
    #         Date of issuance of the bond to override.
    #         Mandatory if instrument code has not been defined.
    #             In case an instrument code has been defined, value comes from bond reference data.
    #         """
    #         self._issue_date = value
    #         return self
    #
    #     def with_end_date(self, value):
    #         """
    #         Maturity date of the bond to override.
    #         Mandatory if instrument code has not been defined and IsPerpetual flag has been set to false.
    #             In case an instrument code has been defined, value comes from bond reference data.
    #         """
    #         self._end_date = value
    #         return self
    #
    #     def with_fixed_rate_percent(self, value):
    #         """
    #         The fixed coupon rate in percentage.
    #         Mandatory in case of a single leg instrument. Otherwise, in case of multi leg instrument, it can be computed as the Par rate.
    #         """
    #         self._fixed_rate_percent = value
    #         return self
    #
    #     def with_interest_calculation_method(self, value):
    #         """
    #         The Day Count Basis method used to calculate the coupon interest payments.
    #         """
    #         if isinstance(value, DayCountBasis):
    #             self._interest_calculation_method = value.value
    #             return self
    #         elif isinstance(value, str):
    #             self._interest_calculation_method = value
    #             return self
    #         raise TypeError("interestCalculationMethod must be a DayCountBasis enum value")
    #
    #     def with_notional_amount(self, value):
    #         """
    #         The notional amount of the leg at the period start date.
    #         Optional. By default 1,000,000 is used.
    #         """
    #         self._notional_amount = value
    #         return self
    #
    #     def with_notional_ccy(self, value):
    #         """
    #         The ISO code of the notional currency.
    #         Mandatory if instrument code or instrument style has not been defined.
    #         In case an instrument code/style has been defined, value may comes from the reference data.
    #         """
    #         self._notional_ccy = value
    #         return self
    #
    #     def with_accrued_calculation_method(self, value):
    #         """
    #         The Day Count Basis method used to calculate the accrued interest payments.
    #         Optional. By default, the same value than DayCountBasis is used.
    #         """
    #         if isinstance(value, DayCountBasis):
    #             self._accrued_calculation_method = value.value
    #             return self
    #         elif isinstance(value, str):
    #             self._accrued_calculation_method = value
    #             return self
    #         raise TypeError("accruedCalculationMethod be a DayCountBasis enum value")
    #
    #     def with_payment_business_day_convention(self, value):
    #         """
    #         The method to adjust dates to a working day.
    #         Optional.
    #             - In case an instrument code/style has been defined, value comes from bond reference data.
    #             - Otherwise MODIFIED_FOLLOWING is used.
    #         """
    #         if isinstance(value, PaymentBusinessDayConvention):
    #             self._payment_business_day_convention = value.value
    #             return self
    #         elif isinstance(value, str):
    #             self._payment_business_day_convention = value
    #             return self
    #         raise TypeError("paymentBusinessDayConvention must be a PaymentBusinessDayConvention enum value")
    #
    #     def with_payment_roll_convention(self, value):
    #         """
    #         Method to get adjust payment dates when they fall at the end of the month (28th of February, 30th, 31st).
    #         Optional. In case an instrument code has been defined, value comes from bond reference data. Otherwise, SAME is used.
    #         """
    #         if isinstance(value, DateRollingConvention):
    #             self._payment_roll_convention = value
    #             return self
    #         elif isinstance(value, str):
    #             self._payment_roll_convention = value
    #             return self
    #         raise TypeError("paymentRollConvention must be a DateRollingConvention enum value")
    #
    #     def with_interest_payment_frequency(self, value):
    #         """
    #         The frequency of the interest payments.
    #         Optional if an instrument code/style have been defined : in that case, value comes from reference data. Otherwise, it is mandatory.
    #         """
    #         if isinstance(value, Frequency):
    #             self._interest_payment_frequency = value.value
    #             return self
    #         elif isinstance(value, str):
    #             self._interest_payment_frequency = value
    #             return self
    #         raise TypeError("interestPaymentFrequency must be a Frequency enum value")
    #
    #     # Future additional Bond definition fields ?
    #     #  (comes from C# project)
    #     #
    #     # def with_isPerpetual(self, value):
    #     #     """
    #     #     Flag the defines wether the bond is perpetual or not in case of user defined bond.
    #     #     Optional. In case an instrument code has been defined, value comes from bond reference data.
    #     #     """
    #     #     self._is_perpetual = value
    #     #     return self
    #     #
    #     # def with_interestType(self, value):
    #     #     """
    #     #     A flag that indicates whether the leg is fixed or float.
    #     #     Mandatory.
    #     #     """
    #     #     if isinstance(value, InterestType):
    #     #         self._interest_type = value
    #     #         return self
    #     #     raise TypeError("interestType must be an InterestType enum value")
    #     #
    #     # def with_indexFixingRic(self, value):
    #     #     """
    #     #     The RIC that carries the fixing value. This value overrides the RIC associated by default with the IndexName and IndexTenor.
    #     #     Optional.
    #     #     """
    #     #     self._index_fixing_ric = value
    #     #     return self
    #     #
    #     # def with_spreadBp(self, value):
    #     #     """
    #     #     The spread in basis point that is added to the floating rate index index value.
    #     #     Optional. By default 0 is used.
    #     #     """
    #     #     self._spread_bp = value
    #     #     return self
    #     #
    #     # def with_indexResetFrequency(self, value):
    #     #     """
    #     #     The reset frequency in case the leg Type is Float.
    #     #     Optional. By default the IndexTenor is used.
    #     #     """
    #     #     if isinstance(value, Frequency):
    #     #         self._index_reset_frequency = value
    #     #         return self
    #     #     raise TypeError("indexResetFrequency must be a Frequency enum value")
    #     #
    #     # def with_indexFixingLag(self, value):
    #     #     """
    #     #     Defines the number of working days between the fixing date and the start of the coupon period ('InAdvance') or the end of the coupon period ('InArrears').
    #     #     Optional. By default 0 is used.
    #     #     """
    #     #     self._index_fixing_lag = value
    #     #     return self
    #     #
    #     # def with_interestPaymentDelay(self, value):
    #     #     """
    #     #     The number of working days between the end of coupon period and the actual interest payment date.
    #     #     Optional. By default no delay (0) is applied.
    #     #     """
    #     #     self._interest_payment_delay = value
    #     #     return self
    #     #
    #     # def with_indexCompoundingMethod(self, value):
    #     #     """
    #     #     A flag that defines how the coupon rate is calculated from the reset floating rates when the reset frequency
    #     #      is higher than the interest payment frequency (e.g. daily index reset with quarterly interest payment).
    #     #     The possible values are:
    #     #         - Compounded (uses the compounded average rate from multiple fixings),
    #     #         - Average (uses the arithmetic average rate from multiple fixings),
    #     #         - Constant (uses the last published rate among multiple fixings),
    #     #         - AdjustedCompounded (uses Chinese 7-day repo fixing),
    #     #         - MexicanCompounded (uses Mexican Bremse fixing).
    #     #     Optional. By default 'Constant' is used.
    #     #     """
    #     #     if isinstance(value, IndexCompoundingMethod):
    #     #         self._index_compounded_method = value
    #     #         return self
    #     #     raise TypeError("indexCompoundingMethod must be an IndexCompoundingMethod enum value")
    #     #
    #     # def with_adjustInterestToPaymentDate(self, value):
    #     #     """
    #     #     A flag that indicates if the coupon dates are adjusted to the payment dates.
    #     #     Optional. By default 'false' is used.
    #     #     """
    #     #     if isinstance(value, AdjustInterestToPaymentDate):
    #     #         self._adjust_interest_to_payment_date = value
    #     #     raise TypeError("adjustInterestToPaymentDate must be an AdjustInterestToPaymentDate enum value")
    #     #
    #     # def with_amortizationSchedule(self, value):
    #     #     """
    #     #     Definition of amortizations
    #     #         type: array
    #     #         items:
    #     #         $ref: '#/definitions/AmortizationItemDefinition'
    #     #     """
    #     #     if isinstance(value, AmortizationItemDefinition):
    #     #         self._amortization_schedule = value
    #     #         return self
    #     #     raise TypeError("amortizationSchedulemust be an AmortizationItemDefinition enum value")
    #     #
    #     # def with_paymentBusinessDays(self, value):
    #     #     """
    #     #     A list of coma-separated calendar codes to adjust dates (e.g. 'EMU' or 'USA').
    #     #     Optional. By default the calendar associated to NotionalCcy is used.
    #     #     """
    #     #     self._payment_business_days = value
    #     #     return self
    #     #
    #     # def with_stubRule(self, value):
    #     #     """
    #     #     The rule that defines whether coupon roll dates are aligned on the  maturity or the issue date.
    #     #     This property may also be used in conjunction with firstRegularPaymentDate and lastRegularPaymentDate; in
    #     #     that case the following values can be defined:
    #     #         - ISSUE : all dates are aligned on the issue date,
    #     #         - MATURITY : all dates are aligned on the maturity date.
    #     #     Optional. By default MATURITY is used.
    #     #     """
    #     #     if isinstance(value, StubRule):
    #     #         self._stub_rule = value
    #     #         return self
    #     #     raise TypeError("stubRule be a StubRule enum value")
    #     #
    #     # def with_firstRegularPaymentDate(self, value):
    #     #     """
    #     #     The first regular coupon payment date for leg with an odd first coupon.
    #     #     Optional.
    #     #     """
    #     #     self._first_regular_payment_date = value
    #     #     return self
    #     #
    #     # def with_lastRegularPaymentDate(self, value):
    #     #     """
    #     #     The last regular coupon payment date for leg with an odd last coupon.
    #     #     Optional.
    #     #     """
    #     #     self._last_regular_payment_date = value
    #     #     return self
    #     #
    #     # def with_direction(self, value):
    #     #     """
    #     #     The direction of the leg.
    #     #     Optional. By default Direction.RECEIVED is used.
    #     #     """
    #     #     if isinstance(value, Direction):
    #     #         self._direction = value
    #     #         return self
    #     #     raise TypeError("direction be a Direction enum value")

    @classmethod
    def get_instrument(cls, params):
        if isinstance(params, Definition.Params):
            return Definition(
                instrument_code=params._instrument_code,
                instrument_tag=params._instrument_tag,
                notional_amount=params._notional_amount,
                fixed_rate_percent=params._fixed_rate_percent,
                issue_date=params._issue_date,
                end_date=params._end_date,
                notional_ccy=params._notional_ccy,
                interest_calculation_method=params._interest_calculation_method,
                accrued_calculation_method=params._accrued_calculation_method,
                payment_business_day_convention=params._payment_business_day_convention,
                payment_roll_convention=params._payment_roll_convention,
            )

    def __init__(
        self,
        instrument_code=None,
        instrument_tag=None,
        notional_amount=None,
        fixed_rate_percent=None,
        issue_date=None,
        end_date=None,
        notional_ccy=None,
        interest_payment_frequency=None,
        interest_calculation_method=None,
        accrued_calculation_method=None,
        payment_business_day_convention=None,
        payment_roll_convention=None,
        first_accrual_date=None,
        template=None,
    ):
        """
        :param instrument_tag: str
        :param instrument_code: str
        :param end_date: str
        :param notional_ccy: str
        :param notional_amount: float
        :param fixed_rate_percent: float
        :param interest_payment_frequency: Frequency
        :param interest_calculation_method: DayCountBasis
        :param accrued_calculation_method: DayCountBasis
        :param payment_business_day_convention: BusinessDayConvention
        :param payment_roll_convention: DateRollingConvention
        :param issue_date: str
        """
        super().__init__(instrument_tag)
        # mandatory values
        self.instrument_code = instrument_code
        self.notional_amount = notional_amount
        self.fixed_rate_percent = fixed_rate_percent
        self.issue_date = issue_date
        self.end_date = end_date
        self.notional_ccy = notional_ccy
        self.interest_payment_frequency = interest_payment_frequency
        self.interest_calculation_method = interest_calculation_method
        self.accrued_calculation_method = accrued_calculation_method
        self.payment_business_day_convention = payment_business_day_convention
        self.payment_roll_convention = payment_roll_convention
        self.first_accrual_date = first_accrual_date
        self.template = template

    @classmethod
    def get_instrument_type(cls):
        return "Bond"

    ##################################
    # Bond definition fields
    ##################################

    @property
    def instrument_code(self):
        """
        Code to define the bond instrument. It can be an ISIN, a RIC or an AssetId .
        :return: string
        """
        return self._get_parameter("instrumentCode")

    @instrument_code.setter
    def instrument_code(self, value):
        self._set_parameter("instrumentCode", value)

    @property
    def issue_date(self):
        """
        Date of issuance of the bond to override.
        Mandatory if instrument code has not been defined.
            In case an instrument code has been defined, value comes from bond reference data.
        :return: datetime
        """
        return self._get_parameter("issueDate")

    @issue_date.setter
    def issue_date(self, value):
        self._set_parameter("issueDate", value)

    @property
    def end_date(self):
        """
        Maturity date of the bond to override.
        Mandatory if instrument code has not been defined and is_perpetual flag has been set to false.
            In case an instrument code has been defined, value comes from bond reference data.
        :return: datetime
        """
        return self._get_parameter("endDate")

    @end_date.setter
    def end_date(self, value):
        self._set_parameter("endDate", value)

    @property
    def fixed_rate_percent(self):
        """
        The fixed coupon rate in percentage.
        Mandatory in case of a single leg instrument. Otherwise, in case of multi leg instrument, it can be computed as the Par rate.
        :return: number
        """
        return self._get_parameter("fixedRatePercent")

    @fixed_rate_percent.setter
    def fixed_rate_percent(self, value):
        self._set_parameter("fixedRatePercent", value)

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
    def accrued_calculation_method(self):
        """
        The Day Count Basis method used to calculate the accrued interest payments.
        Optional. By default, the same value than DayCountBasis is used.
        :return: enum DayCountBasis
        """
        return self._get_enum_parameter(DayCountBasis, "accruedCalculationMethod")

    @accrued_calculation_method.setter
    def accrued_calculation_method(self, value):
        self._set_enum_parameter(DayCountBasis, "accruedCalculationMethod", value)

    @property
    def payment_business_day_convention(self):
        """
        The method to adjust dates to a working day.
        Optional.
            - In case an instrument code/style has been defined, value comes from bond reference data.
            - Otherwise MODIFIED_FOLLOWING is used.
        :return: enum PaymentBusinessDayConvention
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
        Method to get adjust payment dates when they fall at the end of the month (28th of February, 30th, 31st).
        Optional. In case an instrument code has been defined, value comes from bond reference data. Otherwise, SAME is used.
        :return: enum DateRollingConvention
        """
        return self._get_enum_parameter(DateRollingConvention, "paymentRollConvention")

    @payment_roll_convention.setter
    def payment_roll_convention(self, value):
        """
        Method to adjust payment dates when they fall at the end of the month (28th of February, 30th, 31st).
        :param value: enum DateRollingConvention
        """
        self._set_enum_parameter(DateRollingConvention, "paymentRollConvention", value)

    @property
    def interest_payment_frequency(self):
        """
        The frequency of the interest payments.
        Optional if an instrument code/style have been defined : in that case,
        value comes from reference data. Otherwise, it is mandatory.
        :return: enum Frequency
        """
        return self._get_enum_parameter(Frequency, "interestPaymentFrequency")

    @interest_payment_frequency.setter
    def interest_payment_frequency(self, value):
        self._set_enum_parameter(Frequency, "interestPaymentFrequency", value)

    @property
    def first_accrual_date(self):
        """
        Date at which bond starts accruing.
        Optional. In case an instrument code has been defined, value comes from bond reference data. Otherwise default value is the issue date of the bond.
        :return: str
        """
        return self._get_parameter("firstAccrualDate")

    @first_accrual_date.setter
    def first_accrual_date(self, value):
        self._set_parameter("firstAccrualDate", value)

    @property
    def template(self):
        """
        A reference to a Adfin instrument contract or the Adfin detailed contract.
        Optional. Either InstrumentCode, Template, or full definition must be provided.
        :return: str
        """
        return self._get_parameter("template")

    @template.setter
    def template(self, value):
        self._set_parameter("template", value)
