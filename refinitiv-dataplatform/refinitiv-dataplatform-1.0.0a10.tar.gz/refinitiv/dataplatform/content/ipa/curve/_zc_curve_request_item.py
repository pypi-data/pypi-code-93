# coding: utf8
# contract_gen 2020-06-15 10:07:47.574274

__all__ = ["ZcCurveRequestItem"]

from ..instrument._definition import ObjectDefinition
from .zc import ZcCurveMainDefinition
from .zc import ZcCurveMainParameters


class ZcCurveRequestItem(ObjectDefinition):
    def __init__(self, curve_definition=None, curve_parameters=None, curve_tag=None):
        super().__init__()
        self.curve_definition = curve_definition
        self.curve_parameters = curve_parameters
        self.curve_tag = curve_tag

    @property
    def curve_definition(self):
        """
        :return: object ZcCurveMainDefinition
        """
        return self._get_object_parameter(ZcCurveMainDefinition, "curveDefinition")

    @curve_definition.setter
    def curve_definition(self, value):
        self._set_object_parameter(ZcCurveMainDefinition, "curveDefinition", value)

    @property
    def curve_parameters(self):
        """
        :return: object ZcCurveMainParameters
        """
        return self._get_object_parameter(ZcCurveMainParameters, "curveParameters")

    @curve_parameters.setter
    def curve_parameters(self, value):
        self._set_object_parameter(ZcCurveMainParameters, "curveParameters", value)

    @property
    def curve_tag(self):
        """
        :return: str
        """
        return self._get_parameter("curveTag")

    @curve_tag.setter
    def curve_tag(self, value):
        self._set_parameter("curveTag", value)
