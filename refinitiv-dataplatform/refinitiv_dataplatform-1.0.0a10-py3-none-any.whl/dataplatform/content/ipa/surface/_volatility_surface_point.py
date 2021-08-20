# coding: utf8
# contract_gen 2020-05-26 10:37:06.631146

__all__ = ["VolatilitySurfacePoint"]

from refinitiv.dataplatform.content.ipa.instrument._definition import ObjectDefinition


class VolatilitySurfacePoint(ObjectDefinition):
    def __init__(self, x=None, y=None):
        super().__init__()
        self.x = x
        self.y = y

    @property
    def x(self):
        """
        The coordinate of the volatility data point on the x-axis
        :return: str
        """
        return self._get_parameter("x")

    @x.setter
    def x(self, value):
        self._set_parameter("x", value)

    @property
    def y(self):
        """
        The coordinate of the volatility data point on the y-axis
        :return: str
        """
        return self._get_parameter("y")

    @y.setter
    def y(self, value):
        self._set_parameter("y", value)
