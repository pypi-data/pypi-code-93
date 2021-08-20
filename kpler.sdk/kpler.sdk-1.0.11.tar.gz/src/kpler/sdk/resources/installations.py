from pandas import DataFrame

from kpler.sdk import Platform
from kpler.sdk.client import KplerClient
from kpler.sdk.configuration import Configuration


class Installations(KplerClient):
    """
    The ``Installations`` endpoint allows to perform full-text search on installations,
    in order to find names used in Kpler referential.
    """

    RESOURCE_NAME = "installations"

    AVAILABLE_PLATFORMS = [Platform.Dry, Platform.Liquids, Platform.LNG, Platform.LPG]

    def __init__(self, configuration: Configuration, column_ids: bool = True, log_level=None):
        super().__init__(configuration, self.AVAILABLE_PLATFORMS, column_ids, log_level)

    def search(self, q: str) -> DataFrame:
        """

        Args:
            q: str Argument to search by in installation names

        Examples:
            >>> from kpler.sdk.resources.installations import Installations
            ... installations_client=Installations(config)
            ... installations_client.search("abidjan")

            .. csv-table::
                :header: "installations"

                "SIR Abidjan"
                "Abidjan Terminal"

        """
        query_parameters = {"q": q, "resources": self.RESOURCE_NAME}
        return self._search(query_parameters)
