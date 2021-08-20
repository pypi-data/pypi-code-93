# coding: utf8
# contract_gen 2020-06-15 10:07:47.557305

__all__ = ["ForwardCurve"]

from ._curve_definition import CurveDefinition
from ._swap_zc_curve_definition import SwapZcCurveDefinition
from ._swap_zc_curve_parameters import SwapZcCurveParameters
from ._forward_curve_definition import ForwardCurveDefinition


class ForwardCurve(CurveDefinition):
    def __init__(
        self,
        curve_definition=None,
        curve_parameters=None,
        forward_curve_definitions=None,
        curve_tag=None,
    ):
        super().__init__()
        self.curve_definition = curve_definition
        self.curve_parameters = curve_parameters
        self.forward_curve_definitions = forward_curve_definitions
        self.curve_tag = curve_tag

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
    def forward_curve_definitions(self):
        """
        :return: list ForwardCurveDefinition
        """
        return self._get_list_parameter(
            ForwardCurveDefinition, "forwardCurveDefinitions"
        )

    @forward_curve_definitions.setter
    def forward_curve_definitions(self, value):
        self._set_list_parameter(
            ForwardCurveDefinition, "forwardCurveDefinitions", value
        )

    @property
    def curve_tag(self):
        """
        :return: str
        """
        return self._get_parameter("curveTag")

    @curve_tag.setter
    def curve_tag(self, value):
        self._set_parameter("curveTag", value)
