# coding: utf8
# contract_gen 2020-05-19 11:24:17.169985

__all__ = ["NumericalMethod"]

from ..instrument._definition import ObjectDefinition
from ..enum_types.method import Method
from ..models import AmericanMonteCarloParameters
from ..models import PdeParameters


class NumericalMethod(ObjectDefinition):
    def __init__(
        self, american_monte_carlo_parameters=None, method=None, pde_parameters=None
    ):
        super().__init__()
        self.american_monte_carlo_parameters = american_monte_carlo_parameters
        self.method = method
        self.pde_parameters = pde_parameters

    @property
    def american_monte_carlo_parameters(self):
        """
        :return: object AmericanMonteCarloParameters
        """
        return self._get_object_parameter(
            AmericanMonteCarloParameters, "americanMonteCarloParameters"
        )

    @american_monte_carlo_parameters.setter
    def american_monte_carlo_parameters(self, value):
        self._set_object_parameter(
            AmericanMonteCarloParameters, "americanMonteCarloParameters", value
        )

    @property
    def method(self):
        """
        :return: enum Method
        """
        return self._get_enum_parameter(Method, "method")

    @method.setter
    def method(self, value):
        self._set_enum_parameter(Method, "method", value)

    @property
    def pde_parameters(self):
        """
        :return: object PdeParameters
        """
        return self._get_object_parameter(PdeParameters, "pdeParameters")

    @pde_parameters.setter
    def pde_parameters(self, value):
        self._set_object_parameter(PdeParameters, "pdeParameters", value)
