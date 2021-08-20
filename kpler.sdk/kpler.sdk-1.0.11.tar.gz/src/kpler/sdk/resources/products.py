from pandas import DataFrame

from kpler.sdk import Platform
from kpler.sdk.client import KplerClient
from kpler.sdk.configuration import Configuration


class Products(KplerClient):
    """
    The ``Products`` endpoint allows to perform full-text search on products,
    in order to find names used in Kpler referential.
    """

    RESOURCE_NAME = "products"

    AVAILABLE_PLATFORMS = [Platform.Dry, Platform.Liquids, Platform.LNG, Platform.LPG]

    def __init__(self, configuration: Configuration, column_ids: bool = True, log_level=None):
        super().__init__(configuration, self.AVAILABLE_PLATFORMS, column_ids, log_level)

    def search(self, q: str) -> DataFrame:
        """

        Args:
            q: str Argument to search by in products names

        Examples:
            >>> from kpler.sdk.resources.products import Products
            ... products_client=Products(config)
            ... products_client.search("Arab")

            .. csv-table::
                :header: "products"

                "Arab"
                "Arab M"
                "Arab M Abu Safah"
                "Arab SLt."
                "Arab XLt."
                "Arab Hy."
                "Arab Lt."
        """
        query_parameters = {"q": q, "resources": self.RESOURCE_NAME}
        return self._search(query_parameters)
