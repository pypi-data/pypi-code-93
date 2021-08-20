# coding: utf8
# contract_gen 2020-06-15 10:07:47.558275

__all__ = ["SwapZcCurveDefinition"]

from ..instrument._definition import ObjectDefinition
from ..enum_types.asset_class import AssetClass
from ..enum_types.risk_type import RiskType


class SwapZcCurveDefinition(ObjectDefinition):
    def __init__(
        self,
        index_name=None,
        index_tenors=None,
        main_constituent_asset_class=None,
        risk_type=None,
        currency=None,
        discounting_tenor=None,
        id=None,
        name=None,
        source=None,
    ):
        super().__init__()
        self.index_name = index_name
        self.index_tenors = index_tenors
        self.main_constituent_asset_class = main_constituent_asset_class
        self.risk_type = risk_type
        self.currency = currency
        self.discounting_tenor = discounting_tenor
        self.id = id
        self.name = name
        self.source = source

    @property
    def index_tenors(self):
        """
        Defines expected rate surface tenor/slices
        Defaults to the tenors available, based on provided market data
        :return: list string
        """
        return self._get_list_parameter(str, "indexTenors")

    @index_tenors.setter
    def index_tenors(self, value):
        self._set_list_parameter(str, "indexTenors", value)

    @property
    def main_constituent_asset_class(self):
        """
        :return: enum AssetClass
        """
        return self._get_enum_parameter(AssetClass, "mainConstituentAssetClass")

    @main_constituent_asset_class.setter
    def main_constituent_asset_class(self, value):
        self._set_enum_parameter(AssetClass, "mainConstituentAssetClass", value)

    @property
    def risk_type(self):
        """
        :return: enum RiskType
        """
        return self._get_enum_parameter(RiskType, "riskType")

    @risk_type.setter
    def risk_type(self, value):
        self._set_enum_parameter(RiskType, "riskType", value)

    @property
    def currency(self):
        """
        :return: str
        """
        return self._get_parameter("currency")

    @currency.setter
    def currency(self, value):
        self._set_parameter("currency", value)

    @property
    def discounting_tenor(self):
        """
        :return: str
        """
        return self._get_parameter("discountingTenor")

    @discounting_tenor.setter
    def discounting_tenor(self, value):
        self._set_parameter("discountingTenor", value)

    @property
    def id(self):
        """
        Id of the curve definition to get
        :return: str
        """
        return self._get_parameter("id")

    @id.setter
    def id(self, value):
        self._set_parameter("id", value)

    @property
    def index_name(self):
        """
        :return: str
        """
        return self._get_parameter("indexName")

    @index_name.setter
    def index_name(self, value):
        self._set_parameter("indexName", value)

    @property
    def name(self):
        """
        :return: str
        """
        return self._get_parameter("name")

    @name.setter
    def name(self, value):
        self._set_parameter("name", value)

    @property
    def source(self):
        """
        :return: str
        """
        return self._get_parameter("source")

    @source.setter
    def source(self, value):
        self._set_parameter("source", value)
