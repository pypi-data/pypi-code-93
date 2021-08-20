# coding: utf8


__all__ = ["FxBinaryDefinition"]

from ._abstracted_class import BinaryDefinition
from ._settlement_type import SettlementType


class FxBinaryDefinition(BinaryDefinition):
    """"""

    def __init__(
        self,
        binary_type=None,
        payout_amount=None,
        payout_ccy=None,
        settlement_type=None,
        trigger=None,
    ):
        super().__init__()
        self.binary_type = binary_type
        self.payout_amount = payout_amount
        self.payout_ccy = payout_ccy
        self.settlement_type = settlement_type
        self.trigger = trigger

    @property
    def binary_type(self):
        """
        Possible values:
            - None,
            - OneTouchImmediate
            - OneTouchDeferred
            - NoTouch
            - Digital
        :return: enum BinaryType
        """
        from ._fx_binary_type import FxBinaryType

        return self._get_enum_parameter(FxBinaryType, "binaryType")

    @binary_type.setter
    def binary_type(self, value):
        from ._fx_binary_type import FxBinaryType

        self._set_enum_parameter(FxBinaryType, "binaryType", value)

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
        :return: string
        """
        return self._get_enum_parameter(SettlementType, "settlementType")

    @settlement_type.setter
    def settlement_type(self, value):
        self._set_enum_parameter(SettlementType, "settlementType", value)

    @property
    def trigger(self):
        """
        :return: double
        """
        return self._get_parameter("trigger")

    @trigger.setter
    def trigger(self, value):
        self._set_parameter("trigger", value)
