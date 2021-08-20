# coding: utf8


__all__ = ["Definition"]

from refinitiv.dataplatform.tools._common import is_any_defined
from refinitiv.dataplatform import RequiredError
from ...instrument.instrument_definition import InstrumentDefinition
from ._swap_leg_definition import LegDefinition


class Definition(InstrumentDefinition):
    def __init__(
        self,
        *,
        instrument_tag=None,
        trade_date=None,
        start_date=None,
        end_date=None,
        tenor=None,
        settlement_ccy=None,
        is_non_deliverable=None,
        instrument_code=None,
        template=None,
        legs=None,
    ):
        super().__init__()

        error = []
        if not is_any_defined(end_date, tenor):
            error.append("Either the end_date or the tenor must be provided.")

        if not instrument_code:
            error.append(
                "If instrument_code is None, template or legs field must be defined."
            )
            is_any_defined(template, legs) and error.pop()

        if not template:
            error.append(
                "If template is None, instrument_code or legs field must be defined."
            )
            is_any_defined(instrument_code, legs) and error.pop()

        if not legs:
            error.append(
                "If legs is None, the parameter template or instrument_code must be defined."
            )
            is_any_defined(template, instrument_code) and error.pop()

        if error:
            raise RequiredError(-1, error)

        self.instrument_code = instrument_code
        self.instrument_tag = instrument_tag
        self.trade_date = trade_date
        self.start_date = start_date
        self.end_date = end_date
        self.legs = legs
        self.is_non_deliverable = is_non_deliverable
        self.settlement_ccy = settlement_ccy
        self.template = template
        self.tenor = tenor

    @classmethod
    def get_instrument_type(cls):
        return "Swap"

    @property
    def legs(self):
        """
        The legs of the Swap to provide a full definition of the swap if no template or instrumentCode have been provided.
        Optional. Either InstrumentCode, Template, or Legs must be provided.
        :return: list SwapLegDefinition
        """
        return self._get_list_parameter(LegDefinition, "legs")

    @legs.setter
    def legs(self, value):
        self._set_list_parameter(LegDefinition, "legs", value)

    @property
    def end_date(self):
        """
        The maturity date of the swap contract.
        Mandatory. Either the endDate or the tenor must be provided.
        :return: str
        """
        return self._get_parameter("endDate")

    @end_date.setter
    def end_date(self, value):
        self._set_parameter("endDate", value)

    @property
    def instrument_code(self):
        """
        A swap RIC that is used to retrieve the description of the swap contract.
        Optional. Either instrumentCode, template, or legs must be provided.
        :return: str
        """
        return self._get_parameter("instrumentCode")

    @instrument_code.setter
    def instrument_code(self, value):
        self._set_parameter("instrumentCode", value)

    @property
    def is_non_deliverable(self):
        """
        A flag that indicates if the swap is non-deliverable.
        Optional. By defaults 'false'.
        :return: bool
        """
        return self._get_parameter("isNonDeliverable")

    @is_non_deliverable.setter
    def is_non_deliverable(self, value):
        self._set_parameter("isNonDeliverable", value)

    @property
    def settlement_ccy(self):
        """
        For non-deliverable instrument, the ISO code of the settlement currency.
        Optional. By priority order : 'USD' if one leg denominated in USD; 'EUR' if one leg is denominated in EUR; the paidLegCcy.
        :return: str
        """
        return self._get_parameter("settlementCcy")

    @settlement_ccy.setter
    def settlement_ccy(self, value):
        self._set_parameter("settlementCcy", value)

    @property
    def start_date(self):
        """
        The date the swap starts accruing interest. Its effective date.
        Optional. By default it is derived from the TradeDate and the day to spot convention of the contract currency.
        :return: str
        """
        return self._get_parameter("startDate")

    @start_date.setter
    def start_date(self, value):
        self._set_parameter("startDate", value)

    @property
    def template(self):
        """
        A reference to a common swap contract.
        Optional. Either InstrumentCode, Template, or Legs must be provided.
        :return: str
        """
        return self._get_parameter("template")

    @template.setter
    def template(self, value):
        self._set_parameter("template", value)

    @property
    def tenor(self):
        """
        The period code that represents the time between the start date and end date the contract.
        Mandatory. Either the endDate or the tenor must be provided.
        :return: str
        """
        return self._get_parameter("tenor")

    @tenor.setter
    def tenor(self, value):
        self._set_parameter("tenor", value)

    @property
    def trade_date(self):
        """
        The date the swap contract was created.
        Optional. By default the valuation date.
        :return: str
        """
        return self._get_parameter("tradeDate")

    @trade_date.setter
    def trade_date(self, value):
        self._set_parameter("tradeDate", value)
