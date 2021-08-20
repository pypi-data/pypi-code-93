# coding: utf8
# contract_gen 2020-06-15 10:07:47.576305

__all__ = ["ZcCurveDefinition"]

from ..instrument._definition import ObjectDefinition
from ..enum_types.main_constituent_asset_class import MainConstituentAssetClass
from ..enum_types.risk_type import RiskType


class ZcCurveDefinition(ObjectDefinition):
    def __init__(
        self,
        index_name=None,
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
        self.main_constituent_asset_class = main_constituent_asset_class
        self.risk_type = risk_type
        self.currency = currency
        self.discounting_tenor = discounting_tenor
        self.id = id
        self.name = name
        self.source = source

    @property
    def main_constituent_asset_class(self):
        """
        :return: enum AssetClass
        """
        return self._get_enum_parameter(
            MainConstituentAssetClass, "mainConstituentAssetClass"
        )

    @main_constituent_asset_class.setter
    def main_constituent_asset_class(self, value):
        self._set_enum_parameter(
            MainConstituentAssetClass, "mainConstituentAssetClass", value
        )

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
