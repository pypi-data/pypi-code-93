# coding: utf8
# contract_gen 2020-06-15 10:07:47.567306

__all__ = ["ForwardCurveResponseItem"]

from ..instrument._definition import ObjectDefinition
from .swap import SwapZcCurveDefinition
from .swap import SwapZcCurveParameters
from .forward import ForwardCurveItem


class ForwardCurveResponseItem(ObjectDefinition):
    def __init__(
        self,
        instrument_type=None,
        curve_definition=None,
        curve_parameters=None,
        forward_curves=None,
        curve_tag=None,
        request_id=None,
    ):
        super().__init__()
        self.instrument_type = instrument_type
        self.curve_definition = curve_definition
        self.curve_parameters = curve_parameters
        self.forward_curves = forward_curves
        self.curve_tag = curve_tag
        self.request_id = request_id

    @property
    def curve_definition(self):
        """
        :return: object SwapZcCurveDefinition
        """
        return self._get_object_parameter(SwapZcCurveDefinition, "curveDefinition")

    @curve_definition.setter
    def curve_definition(self, value):
        self._set_object_parameter(SwapZcCurveDefinition, "curveDefinition", value)

    @property
    def curve_parameters(self):
        """
        :return: object SwapZcCurveParameters
        """
        return self._get_object_parameter(SwapZcCurveParameters, "curveParameters")

    @curve_parameters.setter
    def curve_parameters(self, value):
        self._set_object_parameter(SwapZcCurveParameters, "curveParameters", value)

    @property
    def forward_curves(self):
        """
        :return: list ForwardCurveItem
        """
        return self._get_list_parameter(ForwardCurveItem, "forwardCurves")

    @forward_curves.setter
    def forward_curves(self, value):
        self._set_list_parameter(ForwardCurveItem, "forwardCurves", value)

    @property
    def curve_tag(self):
        """
        :return: str
        """
        return self._get_parameter("curveTag")

    @curve_tag.setter
    def curve_tag(self, value):
        self._set_parameter("curveTag", value)

    @property
    def instrument_type(self):
        """
        :return: str
        """
        return self._get_parameter("instrumentType")

    @instrument_type.setter
    def instrument_type(self, value):
        self._set_parameter("instrumentType", value)

    @property
    def request_id(self):
        """
        :return: str
        """
        return self._get_parameter("requestId")

    @request_id.setter
    def request_id(self, value):
        self._set_parameter("requestId", value)
