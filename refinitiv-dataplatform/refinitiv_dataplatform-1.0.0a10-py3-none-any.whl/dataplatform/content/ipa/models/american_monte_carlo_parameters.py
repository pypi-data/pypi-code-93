# coding: utf8
# contract_gen 2020-05-19 11:24:17.170985

__all__ = ["AmericanMonteCarloParameters"]

from ..instrument._definition import ObjectDefinition
from ..enum_types.american_monte_carlo_method import AmericanMonteCarloMethod


class AmericanMonteCarloParameters(ObjectDefinition):
    def __init__(
        self,
        american_monte_carlo_method=None,
        additional_points=None,
        all_the_time_points_per_year=None,
        iteration_number=None,
    ):
        super().__init__()
        self.american_monte_carlo_method = american_monte_carlo_method
        self.additional_points = additional_points
        self.all_the_time_points_per_year = all_the_time_points_per_year
        self.iteration_number = iteration_number

    @property
    def american_monte_carlo_method(self):
        """
        :return: enum AmericanMonteCarloMethod
        """
        return self._get_enum_parameter(
            AmericanMonteCarloMethod, "americanMonteCarloMethod"
        )

    @american_monte_carlo_method.setter
    def american_monte_carlo_method(self, value):
        self._set_enum_parameter(
            AmericanMonteCarloMethod, "americanMonteCarloMethod", value
        )

    @property
    def additional_points(self):
        """
        :return: int
        """
        return self._get_parameter("additionalPoints")

    @additional_points.setter
    def additional_points(self, value):
        self._set_parameter("additionalPoints", value)

    @property
    def all_the_time_points_per_year(self):
        """
        :return: int
        """
        return self._get_parameter("allTheTimePointsPerYear")

    @all_the_time_points_per_year.setter
    def all_the_time_points_per_year(self, value):
        self._set_parameter("allTheTimePointsPerYear", value)

    @property
    def iteration_number(self):
        """
        :return: int
        """
        return self._get_parameter("iterationNumber")

    @iteration_number.setter
    def iteration_number(self, value):
        self._set_parameter("iterationNumber", value)
