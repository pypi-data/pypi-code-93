# coding: utf8


__all__ = ["Definition"]

from refinitiv.dataplatform.content.ipa.instrument.instrument_definition import (
    InstrumentDefinition,
)

from ._underlying_type import UnderlyingType


class Definition(InstrumentDefinition):
    #
    # class Params(InstrumentDefinition.Params, abc.ABC):
    #
    #     def __init__(self):
    #         super().__init__()
    #         # common Option fields
    #         self._buy_sell = None
    #         self._call_put = None
    #         self._end_date = None
    #         self._exercise_style = None
    #         self._strike = None
    #         self._underlying_type = None
    #
    #         self._asian_definition = None
    #         self._barrier_definition = None
    #         self._binary_definition = None
    #         self._underlying_definition = None
    #
    #     def with_buy_sell(self, value):
    #         """
    #         The side of the deal.
    #         Possible values:
    #             - Buy
    #             - Sell
    #         """
    #         self._buy_sell = value
    #         return self
    #
    #     def with_call_put(self, value):
    #         """
    #         Tells if the option is a call or a put.
    #         Possible values are:
    #             - Call
    #             - Put
    #
    #         """
    #         self._call_put = value
    #         return self
    #
    #     def with_end_date(self, value):
    #         """
    #         Expiry date of the option
    #         """
    #         self._end_date = value
    #         return self
    #
    #     def with_exercise_style(self, value):
    #         """
    #         Possible values:
    #             - EURO
    #             - AMER
    #             - BERM
    #         """
    #         self._exercise_style = value
    #         return self
    #
    #     def with_strike(self, value):
    #         """
    #         Strike of the option
    #         """
    #         self._strike = value
    #         return self
    #
    #     def with_underlying_type(self, value):
    #         """
    #         Underlying type of the option.
    #         Possible values:
    #             - Eti
    #             - Fx
    #         """
    #         self._underlying_type = value
    #         return self
    #
    #     def with_underlying_definition(self, value):
    #         """
    #         """
    #         self._underlying_definition = value
    #         return self
    #
    # @classmethod
    # def from_params(cls, params):
    #     if isinstance(params, Definition.Params):
    #         return Definition(
    #             instrument_code=params._instrument_code,
    #             instrument_tag=params._instrument_tag,
    #             buy_sell=params._buy_sell,
    #             call_put=params._call_put,
    #             end_date=params._end_date,
    #             exercise_style=params._exercise_style,
    #             strike=params._strike,
    #             underlying_type=params._underlying_type,
    #             underlying_definition=params._underlying_definition,
    #             asian_definition=params._asian_definition,
    #             barrier_definition=params._barrier_definition,
    #             binary_definition=params._binary_definition
    #         )

    def __init__(
        self,
        instrument_code=None,
        instrument_tag=None,
        buy_sell=None,
        call_put=None,
        end_date=None,
        exercise_style=None,
        strike=None,
        underlying_type=UnderlyingType.ETI,
        asian_definition=None,
        barrier_definition=None,
        binary_definition=None,
        cbbc_definition=None,
        deal_contract=None,
        double_barriers_definition=None,
        lot_size=None,
        double_barrier_definition=None,
        double_binary_definition=None,
        dual_currency_definition=None,
        notional_amount=None,
        notional_ccy=None,
        tenor=None,
        underlying_definition=None,
    ):
        super().__init__(instrument_tag)

        # common Option fields
        self.buy_sell = buy_sell
        self.call_put = call_put
        self.end_date = end_date
        self.exercise_style = exercise_style
        self.strike = strike
        self.underlying_type = underlying_type

        # common to Eti and Fx options
        self.asian_definition = asian_definition
        self.barrier_definition = barrier_definition
        self.binary_definition = binary_definition

        # specific to Eti options
        self.cbbc_definition = cbbc_definition
        self.deal_contract = deal_contract
        self.double_barriers_definition = double_barriers_definition
        self.instrument_code = instrument_code
        self.lot_size = lot_size

        # specific to Fx options
        self.double_barrier_definition = double_barrier_definition
        self.double_binary_definition = double_binary_definition
        self.dual_currency_definition = dual_currency_definition
        self.notional_amount = notional_amount
        self.notional_ccy = notional_ccy
        self.tenor = tenor
        self.underlying_definition = underlying_definition
        # self.forward_start_definition = forward_start_definition

    @classmethod
    def get_instrument_type(cls):
        return "Option"

    ##################################
    # Option definition fields
    ##################################

    @property
    def buy_sell(self):
        """
        The side of the deal.
        Possible values:
            - Buy
            - Sell
        :return: string
        """
        return self._get_parameter("buySell")

    @buy_sell.setter
    def buy_sell(self, value):
        self._set_parameter("buySell", value)

    @property
    def call_put(self):
        """
        Tells if the option is a call or a put.
        Possible values:
            - None
            - Call
            - Put
        :return: string
        """
        return self._get_parameter("callPut")

    @call_put.setter
    def call_put(self, value):
        self._set_parameter("callPut", value)

    @property
    def end_date(self):
        """
        Expiry date of the option.
        :return: datetime
        """
        return self._get_parameter("endDate")

    @end_date.setter
    def end_date(self, value):
        self._set_parameter("endDate", value)

    @property
    def exercise_style(self):
        """
        The fixed coupon rate in percentage.
        Mandatory in case of a single leg instrument. Otherwise, in case of multi leg instrument, it can be computed as the Par rate.
        :return: number
        """
        return self._get_parameter("exerciseStyle")

    @exercise_style.setter
    def exercise_style(self, value):
        self._set_parameter("exerciseStyle", value)

    @property
    def strike(self):
        """
        Strike of the option
        :return: float
        """
        return self._get_parameter("strike")

    @strike.setter
    def strike(self, value):
        self._set_parameter("strike", value)

    @property
    def underlying_type(self):
        """
        Underlying type of the option.
        Possible values:
            - Eti
            - Fx
        :return: string
        """
        return self._get_enum_parameter(UnderlyingType, "underlyingType")

    @underlying_type.setter
    def underlying_type(self, value):
        self._set_enum_parameter(UnderlyingType, "underlyingType", value)

    ##########################################
    # Common to Eti and Fx Option properties
    ##########################################
    @property
    def asian_definition(self):
        """
        :return: EtiOptionFixingInfo
        """
        from ._abstracted_class import FixingInfo

        return self._get_object_parameter(FixingInfo, "asianDefinition")

    @asian_definition.setter
    def asian_definition(self, value):
        """"""
        from ._abstracted_class import FixingInfo

        self._set_object_parameter(FixingInfo, "asianDefinition", value)

    @property
    def barrier_definition(self):
        """
        :return: BarrierDefinition
        """
        from ._abstracted_class import BarrierDefinition

        return self._get_object_parameter(BarrierDefinition, "barrierDefinition")

    @barrier_definition.setter
    def barrier_definition(self, value):
        """"""
        from ._abstracted_class import BarrierDefinition

        self._set_object_parameter(BarrierDefinition, "barrierDefinition", value)

    @property
    def binary_definition(self):
        """
        :return: BinaryDefinition
        """
        from ._abstracted_class import BinaryDefinition

        return self._get_object_parameter(BinaryDefinition, "binaryDefinition")

    @binary_definition.setter
    def binary_definition(self, value):
        """"""
        from ._abstracted_class import BinaryDefinition

        self._set_object_parameter(BinaryDefinition, "binaryDefinition", value)

    ##########################################
    # Specific to Eti Option properties
    ##########################################
    @property
    def cbbc_definition(self):
        """
        :return: EtiOptionCBBCDefinition
        """
        from ._cbbc_definition import CBBCDefinition

        return self._get_object_parameter(CBBCDefinition, "cbbcDefinition")

    @cbbc_definition.setter
    def cbbc_definition(self, value):
        """
        :return: EtiOptionCBBCDefinition
        """
        from ._cbbc_definition import CBBCDefinition

        self._set_object_parameter(CBBCDefinition, "cbbcDefinition", value)

    @property
    def deal_contract(self):
        """
        :return: int
        """
        return self._get_parameter("dealContract")

    @deal_contract.setter
    def deal_contract(self, value):
        """"""
        self._set_parameter("dealContract", value)

    @property
    def double_barriers_definition(self):
        """
        :return: EtiDoubleBarriersDefinition
        """
        from ._eti_barrier_definition import EtiDoubleBarriersDefinition

        return self._get_object_parameter(
            EtiDoubleBarriersDefinition, "doubleBarriersDefinition"
        )

    @double_barriers_definition.setter
    def double_barriers_definition(self, value):
        """"""
        from ._eti_barrier_definition import EtiDoubleBarriersDefinition

        self._set_object_parameter(
            EtiDoubleBarriersDefinition, "doubleBarriersDefinition", value
        )

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
    def lot_size(self):
        """
        The lot size. It is the number of options bought or sold in one transaction.
        :return: float
        """
        return self._get_parameter("lotSize")

    @lot_size.setter
    def lot_size(self, value):
        self._set_parameter("lotSize", value)

    ##########################################
    # Specific to Fx Option properties
    ##########################################
    @property
    def double_barrier_definition(self):
        """
        :return: fx.DoubleBarrierDefinition
        """
        from ._double_barrier_definition import DoubleBarrierDefinition

        return self._get_object_parameter(
            DoubleBarrierDefinition, "doubleBarrierDefinition"
        )

    @double_barrier_definition.setter
    def double_barrier_definition(self, value):
        """"""
        from ._double_barrier_definition import DoubleBarrierDefinition

        self._set_object_parameter(
            DoubleBarrierDefinition, "doubleBarrierDefinition", value
        )

    @property
    def double_binary_definition(self):
        """
        :return: fx.DoubleBinaryDefinition
        """
        from ._double_binary_definition import DoubleBinaryDefinition

        return self._get_object_parameter(
            DoubleBinaryDefinition, "doubleBinaryDefinition"
        )

    @double_binary_definition.setter
    def double_binary_definition(self, value):
        """"""
        from ._double_binary_definition import DoubleBinaryDefinition

        self._set_object_parameter(
            DoubleBinaryDefinition, "doubleBinaryDefinition", value
        )

    @property
    def dual_currency_definition(self):
        """
        :return: fx.DualCurrencyDefinition
        """
        from ._dual_currency_definition import DualCurrencyDefinition

        return self._get_object_parameter(
            DualCurrencyDefinition, "dualCurrencyDefinition"
        )

    @dual_currency_definition.setter
    def dual_currency_definition(self, value):
        """
        :return: DoubleBinaryDefinition
        """
        from ._dual_currency_definition import DualCurrencyDefinition

        self._set_object_parameter(
            DualCurrencyDefinition, "dualCurrencyDefinition", value
        )

    @property
    def notional_amount(self):
        """
        The notional amount of currency.
        If the option is a EURGBP Call option, amount of EUR or GBP of the contract.
        :return: float
        """
        return self._get_parameter("notionalAmount")

    @notional_amount.setter
    def notional_amount(self, value):
        """"""
        self._set_parameter("notionalAmount", value)

    @property
    def notional_ccy(self):
        """
        Currency of the notional amount.
        If the option is a EURGBP Call option, notionalCcy can be expressed in EUR OR GBP.
        :return: float
        """
        return self._get_parameter("notionalCcy")

    @notional_ccy.setter
    def notional_ccy(self, value):
        """"""
        self._set_parameter("notionalCcy", value)

    @property
    def tenor(self):
        """
        Tenor of the option.
        :return: string
        """
        return self._get_parameter("tenor")

    @tenor.setter
    def tenor(self, value):
        self._set_parameter("tenor", value)

    @property
    def underlying_definition(self):
        """
        The currency pair.
        Should contain the two currencies, ex EURUSD.
        :return: string
        """
        value = self._get_parameter("underlyingDefinition")
        return value.get("fxCrossCode") if value else None

    @underlying_definition.setter
    def underlying_definition(self, value):
        if value:
            _value = {"fxCrossCode": value}
            self._set_parameter("underlyingDefinition", _value)
        else:
            self._set_parameter("underlyingDefinition", None)
