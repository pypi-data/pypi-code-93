# coding: utf8

__all__ = ["EtiBarrierDefinition", "EtiDoubleBarriersDefinition"]

from refinitiv.dataplatform.content.ipa.instrument._definition import ObjectDefinition
from refinitiv.dataplatform.content.ipa.contracts.option._abstracted_class import (
    BarrierDefinition,
)
from ...enum_types.barrier_style import BarrierStyle


class EtiBarrierDefinition(BarrierDefinition):
    """"""

    def __init__(self, barrier_style=None, in_or_out=None, level=None, up_or_down=None):
        super().__init__()
        self.barrier_style = barrier_style
        self.in_or_out = in_or_out
        self.level = level
        self.up_or_down = up_or_down

    @property
    def barrier_style(self):
        """
        :return: enum BarrierStyle
        """
        return self._get_enum_parameter(BarrierStyle, "barrierStyle")

    @barrier_style.setter
    def barrier_style(self, value):
        self._set_enum_parameter(BarrierStyle, "barrierStyle", value)

    @property
    def in_or_out(self):
        """
        :return: string
        """
        return self._get_parameter("inOrOut")

    @in_or_out.setter
    def in_or_out(self, value):
        self._set_parameter("inOrOut", value)

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
    def up_or_down(self):
        """
        :return: string
        """
        return self._get_parameter("upOrDown")

    @up_or_down.setter
    def up_or_down(self, value):
        self._set_parameter("upOrDown", value)


class EtiDoubleBarriersDefinition(ObjectDefinition):
    def __init__(self, barriers_definition):
        super().__init__()
        self.barriers_definition = barriers_definition

    @property
    def barriers_definition(self):
        """
        :return: list(BarrierDefinition)
        """
        return self._get_list_parameter(BarrierDefinition, "barriersDefinition")

    @barriers_definition.setter
    def barriers_definition(self, value):
        self._set_list_parameter(BarrierDefinition, "barriersDefinition", value)
