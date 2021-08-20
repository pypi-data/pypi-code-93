# coding: utf8
# contract_gen 2020-05-19 11:24:17.154933

__all__ = ["UnderlyingContract"]

from ._repo_underlying_pricing_parameters import UnderlyingCalculationParams
from ...instrument import InstrumentDefinition
from ...instrument._definition import ObjectDefinition


class UnderlyingContract(ObjectDefinition):
    def __init__(
        self,
        instrument_definition=None,
        pricing_parameters=None,
        instrument_type=None,
    ):
        super().__init__()
        self.instrument_type = instrument_type
        self.instrument_definition = instrument_definition
        self.pricing_parameters = pricing_parameters

    @property
    def instrument_definition(self):
        """
        Definition of the input contract
        :return: object InstrumentDefinition
        """
        return self._get_object_parameter(InstrumentDefinition, "instrumentDefinition")

    @instrument_definition.setter
    def instrument_definition(self, value):
        self._set_object_parameter(InstrumentDefinition, "instrumentDefinition", value)

    @property
    def pricing_parameters(self):
        """
        The pricing parameters to apply to this instrument. Optional.
        If pricing parameters are not provided at this level parameters defined globally at the request level are used. If no pricing parameters are provided globally default values apply.
        :return: object RepoUnderlyingPricingParameters
        """
        return self._get_object_parameter(
            UnderlyingCalculationParams, "pricingParameters"
        )

    @pricing_parameters.setter
    def pricing_parameters(self, value):
        self._set_object_parameter(
            UnderlyingCalculationParams, "pricingParameters", value
        )

    @property
    def instrument_type(self):
        """
        The type of instrument being defined.
        :return: str
        """
        return self._get_parameter("instrumentType")

    @instrument_type.setter
    def instrument_type(self, value):
        self._set_parameter("instrumentType", value)
