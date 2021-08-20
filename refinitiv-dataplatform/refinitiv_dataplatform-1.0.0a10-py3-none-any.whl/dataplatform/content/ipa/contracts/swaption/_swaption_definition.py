# coding: utf8
# contract_gen 2020-05-19 11:08:13.668205

__all__ = ["Definition"]

from ._bermudan_swaption_definition import BermudanSwaptionDefinition
from ..swap import Definition as SwapDefinition
from ...enum_types.buy_sell import BuySell
from ...enum_types.call_put import CallPut
from ...enum_types.exercise_style import ExerciseStyle
from ...enum_types.swaption_settlement_type import SwaptionSettlementType
from ...instrument.instrument_definition import InstrumentDefinition


class Definition(InstrumentDefinition):
    def __init__(
        self,
        *,
        instrument_tag=None,
        end_date=None,
        tenor=None,
        bermudan_swaption_definition=None,
        buy_sell,
        call_put,
        exercise_style,
        settlement_type=None,
        underlying_definition,
        strike_percent=None,
    ):
        """
        :param bermudan_swaption_definition: BermudanSwaptionDefinition
        :param buy_sell: BuySell
        :param call_put: CallPut
        :param exercise_style: ExerciseStyle
        :param settlement_type: SwaptionSettlementType
        :param underlying_definition: SwapDefinition
        :param end_date: str
        :param instrument_tag: str
        :param strike_percent: float
        :param tenor: str
        """
        super().__init__()
        self.instrument_tag = instrument_tag
        self.end_date = end_date
        self.tenor = tenor
        self.bermudan_swaption_definition = bermudan_swaption_definition
        self.buy_sell = buy_sell
        self.call_put = call_put
        self.exercise_style = exercise_style
        self.settlement_type = settlement_type
        self.underlying_definition = underlying_definition
        self.strike_percent = strike_percent

    @classmethod
    def get_instrument_type(cls):
        return "Swaption"

    @property
    def bermudan_swaption_definition(self):
        """
        :return: object BermudanSwaptionDefinition
        """
        return self._get_object_parameter(
            BermudanSwaptionDefinition, "bermudanSwaptionDefinition"
        )

    @bermudan_swaption_definition.setter
    def bermudan_swaption_definition(self, value):
        self._set_object_parameter(
            BermudanSwaptionDefinition, "bermudanSwaptionDefinition", value
        )

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
    def call_put(self):
        """
        Tells if the option is a call or a put. Possible values:

         - Call

         - Put
        :return: enum CallPut
        """
        return self._get_enum_parameter(CallPut, "callPut")

    @call_put.setter
    def call_put(self, value):
        self._set_enum_parameter(CallPut, "callPut", value)

    @property
    def exercise_style(self):
        """
        EURO or BERM
        :return: enum ExerciseStyle
        """
        return self._get_enum_parameter(ExerciseStyle, "exerciseStyle")

    @exercise_style.setter
    def exercise_style(self, value):
        self._set_enum_parameter(ExerciseStyle, "exerciseStyle", value)

    @property
    def settlement_type(self):
        """
        The settlement type of the option if the option is exercised
        -Physical
        -Cash
        :return: enum SwaptionSettlementType
        """
        return self._get_enum_parameter(SwaptionSettlementType, "settlementType")

    @settlement_type.setter
    def settlement_type(self, value):
        self._set_enum_parameter(SwaptionSettlementType, "settlementType", value)

    @property
    def underlying_definition(self):
        """
        The details of the underlying swap
        :return: object SwapDefinition
        """
        return self._get_object_parameter(SwapDefinition, "underlyingDefinition")

    @underlying_definition.setter
    def underlying_definition(self, value):
        self._set_object_parameter(SwapDefinition, "underlyingDefinition", value)

    @property
    def end_date(self):
        """
        Expiry date of the option
        :return: str
        """
        return self._get_parameter("endDate")

    @end_date.setter
    def end_date(self, value):
        self._set_parameter("endDate", value)

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
    def strike_percent(self):
        """
        StrikePercent of the option expressed in % format
        :return: float
        """
        return self._get_parameter("strikePercent")

    @strike_percent.setter
    def strike_percent(self, value):
        self._set_parameter("strikePercent", value)

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
