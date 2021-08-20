# coding: utf8
# contract_gen 2020-05-19 11:24:17.155935


__all__ = ["UnderlyingCalculationParams"]

from ...instrument import InstrumentCalculationParams
from ._repo_parameters import RepoParameters
from ..bond import CalculationParams as BondPricingParameters


class UnderlyingCalculationParams(InstrumentCalculationParams):
    def __init__(
        self,
        repo_parameters=None,
        pricing_parameters_at_end=None,
        pricing_parameters_at_start=None,
        valuation_date=None,
    ):
        super().__init__()
        self.pricing_parameters_at_end = pricing_parameters_at_end
        self.pricing_parameters_at_start = pricing_parameters_at_start
        self.repo_parameters = repo_parameters
        self.valuation_date = valuation_date

    @property
    def pricing_parameters_at_end(self):
        """
        Pricing parameters of underlying bond at Repo end date.
        :return: object BondPricingParameters
        """
        return self._get_object_parameter(
            BondPricingParameters, "pricingParametersAtEnd"
        )

    @pricing_parameters_at_end.setter
    def pricing_parameters_at_end(self, value):
        self._set_object_parameter(
            BondPricingParameters, "pricingParametersAtEnd", value
        )

    @property
    def pricing_parameters_at_start(self):
        """
        Pricing parameters of underlying bond at Repo start date.
        :return: object BondPricingParameters
        """
        return self._get_object_parameter(
            BondPricingParameters, "pricingParametersAtStart"
        )

    @pricing_parameters_at_start.setter
    def pricing_parameters_at_start(self, value):
        self._set_object_parameter(
            BondPricingParameters, "pricingParametersAtStart", value
        )

    @property
    def repo_parameters(self):
        """
        Repo parameters to be applied on underlying bond.
        :return: object RepoParameters
        """
        return self._get_object_parameter(RepoParameters, "repoParameters")

    @repo_parameters.setter
    def repo_parameters(self, value):
        self._set_object_parameter(RepoParameters, "repoParameters", value)

    @property
    def valuation_date(self):
        """
        The valuation date for pricing.
        Optional. If not set the valuation date is equal to MarketDataDate or Today. For assets that contains a settlementConvention, the default valuation date  is equal to the settlementdate of the Asset that is usually the TradeDate+SettlementConvention.
        :return: str
        """
        return self._get_parameter("valuationDate")

    @valuation_date.setter
    def valuation_date(self, value):
        self._set_parameter("valuationDate", value)
