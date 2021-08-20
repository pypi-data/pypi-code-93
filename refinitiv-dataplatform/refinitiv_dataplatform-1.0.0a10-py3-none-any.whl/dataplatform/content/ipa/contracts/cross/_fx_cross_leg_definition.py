# coding: utf8
# contract_gen 2020-05-18 08:30:59.278856

__all__ = ["LegDefinition"]

from ...instrument._definition import ObjectDefinition
from ...enum_types.fx_leg_type import FxLegType
from ...enum_types.buy_sell import BuySell


class LegDefinition(ObjectDefinition):
    def __init__(
        self,
        leg_tag=None,
        fx_leg_type=None,
        deal_ccy=None,
        deal_ccy_buy_sell=None,
        deal_amount=None,
        deal_countra_amount=None,
        contra_amount=None,
        end_date=None,
        tenor=None,
        # start_date=None,
        # start_tenor=None,
        # contra_ccy=None,
    ):
        super().__init__()
        self.leg_tag = leg_tag
        self.fx_leg_type = fx_leg_type
        self.deal_ccy = deal_ccy
        self.deal_ccy_buy_sell = deal_ccy_buy_sell
        self.deal_amount = deal_amount
        self.deal_countra_amount = deal_countra_amount
        self.contra_amount = contra_amount
        self.end_date = end_date
        self.tenor = tenor
        # self.start_date = start_date
        # self.start_tenor = start_tenor
        # self.contra_ccy = contra_ccy

    @property
    def deal_ccy_buy_sell(self):
        """
        The direction of the trade in terms of the deal currency : 'Buy' or 'Sell'.
        Optional. Defaults to 'Buy'
        :return: enum BuySell
        """
        return self._get_enum_parameter(BuySell, "dealCcyBuySell")

    @deal_ccy_buy_sell.setter
    def deal_ccy_buy_sell(self, value):
        self._set_enum_parameter(BuySell, "dealCcyBuySell", value)

    @property
    def fx_leg_type(self):
        """
        The enumeration that specifies the type of the leg : 'Spot', 'FxForward', 'FxNonDeliverableForward', 'SwapNear' or 'SwapFar'.
        Mandatory for MultiLeg, FwdFwdSwap, or Swap contracts.
        Optional for Spot and Forwards contracts.
        :return: enum FxLegType
        """
        return self._get_enum_parameter(FxLegType, "fxLegType")

    @fx_leg_type.setter
    def fx_leg_type(self, value):
        self._set_enum_parameter(FxLegType, "fxLegType", value)

    @property
    def contra_amount(self):
        """
        The unsigned amount exchanged to buy or sell the traded amount.
        Optional. By default, it is calculated from the traded rate and the DealAmount. If no traded rate is provided the market rate will be used.
        :return: float
        """
        return self._get_parameter("contraAmount")

    @contra_amount.setter
    def contra_amount(self, value):
        self._set_parameter("contraAmount", value)

    @property
    def deal_countra_amount(self):
        """
        The unsigned amount exchanged to buy or sell the traded amount.
        :return: float
        """
        return self._get_parameter("dealCountraAmount")

    @deal_countra_amount.setter
    def deal_countra_amount(self, value):
        self._set_parameter("dealCountraAmount", value)

    # @property
    # def contra_ccy(self):
    #     """
    #     The currency that is exchanged.
    #     Optional. By default, the second currency in the FxCrossCode.
    #     :return: str
    #     """
    #     return self._get_parameter("contraCcy")
    #
    # @contra_ccy.setter
    # def contra_ccy(self, value):
    #     self._set_parameter("contraCcy", value)

    @property
    def deal_amount(self):
        """
        The unsigned amount of traded currency actually bought or sold.
        Optional. Defaults to 1,000,000'.
        :return: float
        """
        return self._get_parameter("dealAmount")

    @deal_amount.setter
    def deal_amount(self, value):
        self._set_parameter("dealAmount", value)

    @property
    def deal_ccy(self):
        """
        The ISO code of the traded currency (e.g. 'EUR' ).
        Optional. Defaults to the first currency of the FxCrossCode.
        :return: str
        """
        return self._get_parameter("dealCcy")

    @deal_ccy.setter
    def deal_ccy(self, value):
        self._set_parameter("dealCcy", value)

    @property
    def end_date(self):
        """
        The maturity date of the contract that is the date the amounts are exchanged.
        Either the EndDate or the Tenor must be provided.
        :return: str
        """
        return self._get_parameter("endDate")

    @end_date.setter
    def end_date(self, value):
        self._set_parameter("endDate", value)

    @property
    def leg_tag(self):
        """
        A user defined string to identify the leg.
        Optional.
        :return: str
        """
        return self._get_parameter("legTag")

    @leg_tag.setter
    def leg_tag(self, value):
        self._set_parameter("legTag", value)

    # @property
    # def start_date(self):
    #     """
    #     :return: str
    #     """
    #     return self._get_parameter("startDate")
    #
    # @start_date.setter
    # def start_date(self, value):
    #     self._set_parameter("startDate", value)

    # @property
    # def start_tenor(self):
    #     """
    #     The tenor representing the Starting of maturity period of the contract (e.g. '1Y' or '6M' ).
    #     Either the StartDate or the StartTenor must be provided for TimeOptionForward.
    #     :return: str
    #     """
    #     return self._get_parameter("startTenor")
    #
    # @start_tenor.setter
    # def start_tenor(self, value):
    #     self._set_parameter("startTenor", value)

    @property
    def tenor(self):
        """
        The tenor representing the maturity date of the contract (e.g. '1Y' or '6M' ).
        Either the EndDate or the Tenor must be provided.
        :return: str
        """
        return self._get_parameter("tenor")

    @tenor.setter
    def tenor(self, value):
        self._set_parameter("tenor", value)
