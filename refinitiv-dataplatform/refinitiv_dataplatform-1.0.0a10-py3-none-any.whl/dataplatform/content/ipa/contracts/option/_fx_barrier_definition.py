# coding: utf8


__all__ = ["FxBarrierDefinition"]

from refinitiv.dataplatform.content.ipa.enum_types import BarrierMode
from ._abstracted_class import BarrierDefinition


class FxBarrierDefinition(BarrierDefinition):
    """"""

    def __init__(
        self,
        barrier_mode=None,
        in_or_out=None,
        level=None,
        rebate_amount=None,
        up_or_down=None,
        window_start_date=None,
        window_end_date=None,
    ):
        super().__init__()
        self.barrier_mode = barrier_mode
        self.in_or_out = in_or_out
        self.level = level
        self.rebate_amount = rebate_amount
        self.up_or_down = up_or_down
        self.window_start_date = window_start_date
        self.window_end_date = window_end_date

    @property
    def barrier_mode(self):
        """
        Barrier Mode of the barrier option.
        Possible values :
            - Undefined
            - European
            - American
            - ForwardStartWindow
            - EarlyEndWindow
        :return: enum fx.BarrierMode
        """
        return self._get_enum_parameter(BarrierMode, "barrierMode")

    @barrier_mode.setter
    def barrier_mode(self, value):
        self._set_enum_parameter(BarrierMode, "barrierMode", value)

    @property
    def in_or_out(self):
        """
        In/Out property of the barrier option
        :return: string
        """
        return self._get_parameter("inOrOut")

    @in_or_out.setter
    def in_or_out(self, value):
        self._set_parameter("inOrOut", value)

    @property
    def level(self):
        """
        Barrier of the barrier option
        :return: double
        """
        return self._get_parameter("level")

    @level.setter
    def level(self, value):
        self._set_parameter("level", value)

    @property
    def rebate_amount(self):
        """
        Rebate of the barrier option
        :return: double
        """
        return self._get_parameter("rebateAmount")

    @rebate_amount.setter
    def rebate_amount(self, value):
        self._set_parameter("rebateAmount", value)

    @property
    def up_or_down(self):
        """
        Up/Down property of the barrier option.
        :return: string
        """
        return self._get_parameter("upOrDown")

    @up_or_down.setter
    def up_or_down(self, value):
        self._set_parameter("upOrDown", value)

    @property
    def window_start_date(self):
        """
        Up/Down property of the barrier option.
        :return: string
        """
        return self._get_parameter("windowStartDate")

    @window_start_date.setter
    def window_start_date(self, value):
        self._set_parameter("windowStartDate", value)

    @property
    def window_end_date(self):
        """
        Up/Down property of the barrier option.
        :return: string
        """
        return self._get_parameter("windowEndDate")

    @window_end_date.setter
    def window_end_date(self, value):
        self._set_parameter("windowEndDate", value)
