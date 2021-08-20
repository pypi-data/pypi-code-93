# coding: utf8
# contract_gen 2020-05-13 12:48:48.786015


__all__ = ["Definition"]

from refinitiv.dataplatform import RequiredError
from refinitiv.dataplatform.tools._common import is_all_defined, is_any_defined
from ._premium_leg_definition import PremiumLegDefinition
from ._protection_leg_definition import ProtectionLegDefinition
from ...enum_types.cds_convention import CdsConvention
from ...enum_types.business_day_convention import BusinessDayConvention
from ...instrument.instrument_definition import InstrumentDefinition


class Definition(InstrumentDefinition):
    def __init__(
        self,
        *,
        instrument_tag,
        instrument_code=None,
        cds_convention,
        trade_date,
        step_in_date,
        start_date,
        end_date=None,
        tenor=None,
        start_date_moving_convention=None,
        end_date_moving_convention,
        adjust_to_isda_end_date,
        protection_leg=None,
        premium_leg=None,
        accrued_begin_date=None,
    ):
        super().__init__()

        error = []
        if not instrument_code:
            error.append(
                "If instrument_code is null, the protection_leg and the premium_leg must be provided."
            )
            is_all_defined(premium_leg, protection_leg) and error.pop()

        if not instrument_code:
            error.append(
                "If instrument_code is null, either the end_date or the tenor must be provided."
            )
            is_any_defined(end_date, tenor) and error.pop()

        # if is_all_defined(instrument_code, premium_leg, protection_leg):
        #     error.append("Provide premium_leg and protection_leg only if instrument_code is not defined.")

        if error:
            raise RequiredError(-1, error)

        self.instrument_tag = instrument_tag
        self.instrument_code = instrument_code
        self.cds_convention = cds_convention
        self.trade_date = trade_date
        self.step_in_date = step_in_date
        self.start_date = start_date
        self.end_date = end_date
        self.tenor = tenor
        self.start_date_moving_convention = start_date_moving_convention
        self.end_date_moving_convention = end_date_moving_convention
        self.adjust_to_isda_end_date = adjust_to_isda_end_date
        self.protection_leg = protection_leg
        self.premium_leg = premium_leg
        self.accrued_begin_date = accrued_begin_date

    @classmethod
    def get_instrument_type(cls):
        return "Cds"

    @property
    def cds_convention(self):
        """
        Define the cds convention. Possible values are:

         - 'ISDA' (startDate will default to accruedBeginDate, endDate will be adjusted to IMM Date),

         - 'UserDefined' (startDate will default to stepInDate, endDate will not be adjusted).

        Optional. Defaults to 'ISDA'.
        :return: enum CdsConvention
        """
        return self._get_enum_parameter(CdsConvention, "cdsConvention")

    @cds_convention.setter
    def cds_convention(self, value):
        self._set_enum_parameter(CdsConvention, "cdsConvention", value)

    @property
    def end_date_moving_convention(self):
        """
        The method to adjust the endDate..
        The possible values are:
         - ModifiedFollowing (adjusts dates according to the Modified Following convention - next business day unless is it goes into the next month, preceeding is used in that  case),
         - NextBusinessDay (adjusts dates according to the Following convention - Next Business Day),
         - PreviousBusinessDay (adjusts dates  according to the Preceeding convention - Previous Business Day),
         - NoMoving (does not adjust dates),
         - BbswModifiedFollowing (adjusts dates  according to the BBSW Modified Following convention).
        Optional. By default 'NoMoving' is used.
        :return: enum BusinessDayConvention
        """
        return self._get_enum_parameter(
            BusinessDayConvention, "endDateMovingConvention"
        )

    @end_date_moving_convention.setter
    def end_date_moving_convention(self, value):
        self._set_enum_parameter(
            BusinessDayConvention, "endDateMovingConvention", value
        )

    @property
    def premium_leg(self):
        """
        The Premium Leg of the CDS. It is a swap leg paying a fixed coupon.
        Mandatory if instrumenCode is null.
        Optional if instrumentCode not null.
        :return: object PremiumLegDefinition
        """
        return self._get_object_parameter(PremiumLegDefinition, "premiumLeg")

    @premium_leg.setter
    def premium_leg(self, value):
        self._set_object_parameter(PremiumLegDefinition, "premiumLeg", value)

    @property
    def protection_leg(self):
        """
        The Protection Leg of the CDS. It is the default leg.
        Mandatory if instrumenCode is null.
        Optional if instrumentCode not null.
        :return: object ProtectionLegDefinition
        """
        return self._get_object_parameter(ProtectionLegDefinition, "protectionLeg")

    @protection_leg.setter
    def protection_leg(self, value):
        self._set_object_parameter(ProtectionLegDefinition, "protectionLeg", value)

    @property
    def start_date_moving_convention(self):
        """
        The method to adjust the startDate.
        The possible values are:
         - ModifiedFollowing (adjusts dates according to the Modified Following convention - next business day unless is it goes into the next month, preceeding is used in that  case),
         - NextBusinessDay (adjusts dates according to the Following convention - Next Business Day),
         - PreviousBusinessDay (adjusts dates  according to the Preceeding convention - Previous Business Day),
         - NoMoving (does not adjust dates),
         - BbswModifiedFollowing (adjusts dates  according to the BBSW Modified Following convention).
        Optional. By default 'NoMoving' is used.
        :return: enum BusinessDayConvention
        """
        return self._get_enum_parameter(
            BusinessDayConvention, "startDateMovingConvention"
        )

    @start_date_moving_convention.setter
    def start_date_moving_convention(self, value):
        self._set_enum_parameter(
            BusinessDayConvention, "startDateMovingConvention", value
        )

    @property
    def accrued_begin_date(self):
        """
        The last cashflow date.
        Optional. By default it is the last cashflow date.
        :return: str
        """
        return self._get_parameter("accruedBeginDate")

    @accrued_begin_date.setter
    def accrued_begin_date(self, value):
        self._set_parameter("accruedBeginDate", value)

    @property
    def adjust_to_isda_end_date(self):
        """
        The way the endDate is adjusted if computed from tenor input.
          The possible values are:
         - true ( the endDate is an IMM date computed from startDate according to ISDA rules, ),
         - false ( the endDate is computed from startDate according to endDateMovingConvention),
        Optional. By default true is used if cdsConvention is ISDA, else false is used.
        :return: bool
        """
        return self._get_parameter("adjustToIsdaEndDate")

    @adjust_to_isda_end_date.setter
    def adjust_to_isda_end_date(self, value):
        self._set_parameter("adjustToIsdaEndDate", value)

    @property
    def end_date(self):
        """
        The maturity date of the cds contract.
        Mandatory if instrumentCode is null. Either the endDate or the tenor must be provided.
        :return: str
        """
        return self._get_parameter("endDate")

    @end_date.setter
    def end_date(self, value):
        self._set_parameter("endDate", value)

    @property
    def instrument_code(self):
        """
        A cds RIC that is used to retrieve the description of the cds contract.
        Optional. If null, the protectionLeg and the premiumLeg  must be provided.
        :return: str
        """
        return self._get_parameter("instrumentCode")

    @instrument_code.setter
    def instrument_code(self, value):
        self._set_parameter("instrumentCode", value)

    @property
    def start_date(self):
        """
        The date the cds starts accruing interest. Its effective date.
        Optional. By default it is the accruedBeginDate (the last IMM date before tradeDate) if cdsConvention is ISDA, else it is the stepInDate.
        :return: str
        """
        return self._get_parameter("startDate")

    @start_date.setter
    def start_date(self, value):
        self._set_parameter("startDate", value)

    @property
    def step_in_date(self):
        """
        The effective protection date.
        Optional. By default the tradeDate + 1 calendar.
        :return: str
        """
        return self._get_parameter("stepInDate")

    @step_in_date.setter
    def step_in_date(self, value):
        self._set_parameter("stepInDate", value)

    @property
    def tenor(self):
        """
        The period code that represents the time between the start date and end date the contract.
        Mandatory if instrumentCode is null. Either the endDate or the tenor must be provided.
        :return: str
        """
        return self._get_parameter("tenor")

    @tenor.setter
    def tenor(self, value):
        self._set_parameter("tenor", value)

    @property
    def trade_date(self):
        """
        The date the cds contract was created.
        Optional. By default the valuation date.
        :return: str
        """
        return self._get_parameter("tradeDate")

    @trade_date.setter
    def trade_date(self, value):
        self._set_parameter("tradeDate", value)
