# coding: utf8


__all__ = ["EtiBinaryDefinition"]

from ._abstracted_class import BinaryDefinition
from ._eti_binary_type import EtiBinaryType


class EtiBinaryDefinition(BinaryDefinition):
    """"""

    def __init__(
        self, binary_type=None, level=None, notional_amount=None, up_or_down=None
    ):
        super().__init__()
        self.binary_type = binary_type
        self.level = level
        self.notional_amount = notional_amount
        self.up_or_down = up_or_down

    @property
    def binary_type(self):
        """
        Possible values:
            - None,
            - OneTouch
            - NoTouch
            - Digital
        :return: string
        """
        return self._get_enum_parameter(EtiBinaryType, "binaryType")

    @binary_type.setter
    def binary_type(self, value):
        self._set_enum_parameter(EtiBinaryType, "binaryType", value)

    @property
    def level(self):
        """
        :return: double
        """
        return self._get_parameter("level")

    @level.setter
    def level(self, value):
        self._set_parameter("level", value)

    @property
    def notional_amount(self):
        """
        :return: double
        """
        return self._get_parameter("notionalAmount")

    @notional_amount.setter
    def notional_amount(self, value):
        self._set_parameter("notionalAmount", value)

    @property
    def up_or_down(self):
        """
        :return: string
        """
        return self._get_parameter("upOrDown")

    @up_or_down.setter
    def up_or_down(self, value):
        self._set_parameter("upOrDown", value)
