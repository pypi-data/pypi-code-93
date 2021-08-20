# coding: utf8
# contract_gen 2020-06-16 10:26:10.741158

__all__ = ["BaseDefinition"]

import abc

import numpy as np
from scipy import interpolate
import pandas as pd

from refinitiv.dataplatform.delivery.data.endpoint import Endpoint
from ._surface_output import SurfaceOutput
from ..enum_types.underlying_type import UnderlyingType
from ..enum_types.axis import Axis
from ..instrument._definition import ObjectDefinition


def parse_axis(universe):
    surface = universe.get("surface")

    strike_axis = surface[0][1:]
    surface = surface[1:]
    time_axis = []
    surface_grid = []

    for curve in surface:
        time_axis.append(curve[0])
        surface_grid.append(curve[1:])

    x = np.array(strike_axis, dtype=float)
    y = np.array(time_axis, dtype="datetime64")
    Z = np.array(surface_grid, dtype=float)
    X, Y = np.meshgrid(x, y)
    return X, Y, Z


def interpolate_data(x, y, z, x_value, y_value):
    x_axis = x[0]
    y_axis = y[:, 0]
    if isinstance(y_value, str):
        y_value = np.datetime64(y_value)
    return interpolate.interp2d(x_axis, y_axis.astype(int), z)(
        x_value, y_value.astype(int)
    )


class BaseDefinition(ObjectDefinition, abc.ABC):
    class Surface(object):
        def __init__(self, x, y, z):
            super().__init__()
            self.x = x
            self.y = y
            self.z = z

        def get_axis(self):
            return self.x, self.y, self.z

        def get_curve(self, value, axis_type):
            axis = []
            curve = None

            if axis_type is Axis.X:
                axis = self.x[0]
            elif axis_type is Axis.Y:
                axis = np.array([str(i) for i in self.y[:, 0]])
            elif axis_type is Axis.Z:
                axis = self.z

            if value not in axis:
                # interpolate
                if axis_type is Axis.X:
                    curve_y = self.y[:, 0]
                    curve_z = interpolate_data(self.x, self.y, self.z, value, curve_y)[
                        :, 0
                    ]
                    curve = curve_y, curve_z
                elif axis_type is Axis.Y:
                    curve_x = self.x[0, :]
                    curve_z = interpolate_data(self.x, self.y, self.z, curve_x, value)
                    curve = curve_x, curve_z
            else:
                if axis_type is Axis.X:
                    index = np.where(axis == value)[0][0]
                    curve_y = self.y[:, index]
                    curve_z = self.z[:, index]
                    curve = curve_y, curve_z
                elif axis_type is Axis.Y:
                    index = np.where(axis == value)[0][0]
                    curve_x = self.x[index, :]
                    curve_z = self.z[index, :]
                    curve = curve_x, curve_z

            return curve

        def get_point(self, x, y):
            point = None

            if x in self.x and np.datetime64(y) in self.y:
                index1 = np.where(self.x == x)[1][0]
                index2 = np.where(self.y == np.datetime64(y))[0][0]
                point = self.z[index2][index1]
            else:
                # interpolate
                point = interpolate_data(self.x, self.y, self.z, x, y)[0]
            return point

    class Data(Endpoint.EndpointData):
        def __init__(self, raw, surface=None):
            super().__init__(raw)
            self._surface = surface

        @property
        def surface(self):
            if self._surface is None and self._raw:
                universe = self._raw.get("data")[0]
                self._surface = BaseDefinition.Surface(*parse_axis(universe))
            return self._surface

        @property
        def df(self):
            if self._dataframe is None and self._raw:
                data_frame = None
                if False:
                    dfs = []

                    for universe in self._raw.get("data"):
                        surface_tag = universe.get("surfaceTag")
                        x, y, z = parse_axis(universe)
                        index = pd.MultiIndex.from_product([[surface_tag], ["x", "y"]])
                        df = pd.DataFrame([x, y], index=index)
                        dfs.append(df)
                    data_frame = pd.concat(dfs)
                else:
                    data = self._raw.get("data")
                    if data:
                        data_frame = pd.DataFrame(data)
                    else:
                        data_frame = pd.DataFrame([])
                if not data_frame.empty:
                    data_frame = data_frame.convert_dtypes()
                self._dataframe = data_frame
            return self._dataframe

    class Response(Endpoint.EndpointResponse):
        def __init__(self, response):
            super().__init__(response, service_class=BaseDefinition)
            _raw_json = self.data.raw if self.data else None
            if self.is_success:
                _error = _raw_json["data"][0].get("error", "")
                if _error:
                    self._status = _error["status"]
                    if self._status == "Error":
                        self._is_success = False
                        self._error_code = _error["code"]
                        self._error_message = _error["message"]

    def __init__(
        self,
        underlying_type,
        tag,
        layout,
    ):
        super().__init__()
        self.tag = tag
        self.layout = layout
        self.underlying_type = underlying_type

    @property
    def layout(self):
        """
        The section that contains the properties that define how the volatility surface is returned
        :return: object SurfaceOutput
        """
        return self._get_object_parameter(SurfaceOutput, "surfaceLayout")

    @layout.setter
    def layout(self, value):
        self._set_object_parameter(SurfaceOutput, "surfaceLayout", value)

    @property
    def underlying_type(self):
        """
        The type of the underlying used to generate the volatility surface
        :return: enum UnderlyingType
        """
        return self._get_enum_parameter(UnderlyingType, "underlyingType")

    @underlying_type.setter
    def underlying_type(self, value):
        self._set_enum_parameter(UnderlyingType, "underlyingType", value)

    @property
    def tag(self):
        """
        A user defined string to describe the volatility surface
        :return: str
        """
        return self._get_parameter("surfaceTag")

    @tag.setter
    def tag(self, value):
        self._set_parameter("surfaceTag", value)
