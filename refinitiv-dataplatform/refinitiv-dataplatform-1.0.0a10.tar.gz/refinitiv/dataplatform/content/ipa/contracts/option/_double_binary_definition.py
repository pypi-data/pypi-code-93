# coding: utf8


__all__ = ["DoubleBinaryDefinition"]


from refinitiv.dataplatform.content.ipa.instrument._definition import ObjectDefinition


class DoubleBinaryDefinition(ObjectDefinition):
    """"""

    def __init__(
        self,
        double_binary_type=None,
        payout_amount=None,
        payout_ccy=None,
        settlement_type=None,
        trigger_down=None,
        trigger_up=None,
    ):
        super().__init__()
        self.double_binary_type = double_binary_type
        self.payout_amount = payout_amount
        self.payout_ccy = payout_ccy
        self.settlement_type = settlement_type
        self.trigger_down = trigger_down
        self.trigger_up = trigger_up

    @property
    def double_binary_type(self):
        """
        Possible values:
            - None,
            - DoubleNoTouch
        :return: fx.DoubleBinaryType
        """
        from refinitiv.dataplatform.content.ipa.contracts.option._double_binary_type import (
            DoubleBinaryType,
        )

        return self._get_enum_parameter(DoubleBinaryType, "binaryType")

    @double_binary_type.setter
    def double_binary_type(self, value):
        from refinitiv.dataplatform.content.ipa.contracts.option._double_binary_type import (
            DoubleBinaryType,
        )

        self._set_enum_parameter(DoubleBinaryType, "binaryType", value)

    @property
    def payout_amount(self):
        """
        :return: double
        """
        return self._get_parameter("payoutAmount")

    @payout_amount.setter
    def payout_amount(self, value):
        self._set_parameter("payoutAmount", value)

    @property
    def payout_ccy(self):
        """
        :return: string
        """
        return self._get_parameter("payoutCcy")

    @payout_ccy.setter
    def payout_ccy(self, value):
        self._set_parameter("payoutCcy", value)

    @property
    def settlement_type(self):
        """
        Settlement Type of the BinaryOption
        Possible values :
            - Undefined
            - Cash
            - Asset
        :return: enum fx.SettlementType
        """
        from ._settlement_type import SettlementType

        return self._get_enum_parameter(SettlementType, "settlementType")

    @settlement_type.setter
    def settlement_type(self, value):
        from ._settlement_type import SettlementType

        self._set_enum_parameter(SettlementType, "settlementType", value)

    @property
    def trigger_down(self):
        """
        Barrier Down for the Double Barrier option
        :return: double
        """
        return self._get_parameter("triggerDown")

    @trigger_down.setter
    def trigger_down(self, value):
        self._set_parameter("triggerDown", value)

    @property
    def trigger_up(self):
        """
        Barrier Up for the Double Barrier option
        :return: double
        """
        return self._get_parameter("triggerUp")

    @trigger_up.setter
    def trigger_up(self, value):
        self._set_parameter("triggerUp", value)
