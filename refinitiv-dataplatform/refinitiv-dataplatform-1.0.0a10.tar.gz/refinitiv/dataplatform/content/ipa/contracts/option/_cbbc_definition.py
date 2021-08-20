# coding: utf8


__all__ = ["CBBCDefinition"]

from refinitiv.dataplatform.content.ipa.instrument._definition import ObjectDefinition


class CBBCDefinition(ObjectDefinition):
    """"""

    def __init__(self, conversion_ratio=None, level=None):
        super().__init__()
        self.conversion_ratio = conversion_ratio
        self.level = level

    @property
    def conversion_ratio(self):
        """
        :return: string
        """
        return self._get_parameter("conversionRatio")

    @conversion_ratio.setter
    def conversion_ratio(self, value):
        self._set_parameter("conversionRatio", value)

    @property
    def level(self):
        """
        :return: double
        """
        return self._get_parameter("level")

    @level.setter
    def level(self, value):
        self._set_parameter("level", value)
