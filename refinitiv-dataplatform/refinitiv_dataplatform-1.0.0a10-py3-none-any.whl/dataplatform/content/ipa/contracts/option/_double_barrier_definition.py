# coding: utf8


__all__ = ["DoubleBarrierDefinition"]

from refinitiv.dataplatform.content.ipa.instrument._definition import ObjectDefinition


class DoubleBarrierDefinition(ObjectDefinition):
    """"""

    def __init__(self, barrier_down=None, barrier_mode=None, barrier_up=None):
        super().__init__()
        self.barrier_down = barrier_down
        self.barrier_mode = barrier_mode
        self.barrier_up = barrier_up

    @property
    def barrier_down(self):
        """
        :return: enum fx.DoubleBarrierInfo
        """
        from refinitiv.dataplatform.content.ipa.contracts.option import (
            DoubleBarrierInfo,
        )

        return self._get_object_parameter(DoubleBarrierInfo, "barrierDown")

    @barrier_down.setter
    def barrier_down(self, value):
        from refinitiv.dataplatform.content.ipa.contracts.option import (
            DoubleBarrierInfo,
        )

        self._set_object_parameter(DoubleBarrierInfo, "barrierDown", value)

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
        from refinitiv.dataplatform.content.ipa.enum_types import BarrierMode

        return self._get_enum_parameter(BarrierMode, "barrierMode")

    @barrier_mode.setter
    def barrier_mode(self, value):
        from refinitiv.dataplatform.content.ipa.enum_types import BarrierMode

        self._set_enum_parameter(BarrierMode, "barrierMode", value)

    @property
    def barrier_up(self):
        """
        :return: enum fx.DoubleBarrierInfo
        """
        from ._double_barrier_info import DoubleBarrierInfo

        return self._get_object_parameter(DoubleBarrierInfo, "barrierUp")

    @barrier_up.setter
    def barrier_up(self, value):
        from ._double_barrier_info import DoubleBarrierInfo

        self._set_object_parameter(DoubleBarrierInfo, "barrierUp", value)
