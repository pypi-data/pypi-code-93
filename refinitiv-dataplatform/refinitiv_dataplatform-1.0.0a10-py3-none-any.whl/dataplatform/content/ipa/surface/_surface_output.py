# coding: utf8
# contract_gen 2020-05-26 10:37:06.630147

__all__ = ["SurfaceOutput"]

from refinitiv.dataplatform.content.ipa.instrument._definition import ObjectDefinition
from ._volatility_surface_point import VolatilitySurfacePoint
from ..enum_types.format import Format


class SurfaceOutput(ObjectDefinition):
    def __init__(
        self,
        data_points=None,
        format=None,
        x_values=None,
        y_values=None,
        x_point_count=None,
        y_point_count=None,
    ):
        super().__init__()
        self.data_points = data_points
        self.format = format
        self.x_values = x_values
        self.y_values = y_values
        self.x_point_count = x_point_count
        self.y_point_count = y_point_count

    @property
    def data_points(self):
        """
        Specifies the list of specific data points to be returned.
        :return: list VolatilitySurfacePoint
        """
        return self._get_list_parameter(VolatilitySurfacePoint, "dataPoints")

    @data_points.setter
    def data_points(self, value):
        self._set_list_parameter(VolatilitySurfacePoint, "dataPoints", value)

    @property
    def format(self):
        """
        Specifies whether the calculated volatilities are returned as a list or a matrix.
        :return: enum Format
        """
        return self._get_enum_parameter(Format, "format")

    @format.setter
    def format(self, value):
        self._set_enum_parameter(Format, "format", value)

    @property
    def x_values(self):
        """
        Specifies a list of discrete values for the x-axis.
        :return: list string
        """
        return self._get_list_parameter(str, "xValues")

    @x_values.setter
    def x_values(self, value):
        self._set_list_parameter(str, "xValues", value)

    @property
    def y_values(self):
        """
        Specifies a list of discrete values for the y-axis.
        :return: list string
        """
        return self._get_list_parameter(str, "yValues")

    @y_values.setter
    def y_values(self, value):
        self._set_list_parameter(str, "yValues", value)

    @property
    def x_point_count(self):
        """
        Specifies the number of values that will be generated along the x-axis.
        These values will distributed depending on the available input data and the type of volatility.
        :return: int
        """
        return self._get_parameter("xPointCount")

    @x_point_count.setter
    def x_point_count(self, value):
        self._set_parameter("xPointCount", value)

    @property
    def y_point_count(self):
        """
        Specifies the number of values that will be generated along the y-axis.
        These values will distributed depending on the available input data and the type of volatility.
        :return: int
        """
        return self._get_parameter("yPointCount")

    @y_point_count.setter
    def y_point_count(self, value):
        self._set_parameter("yPointCount", value)
