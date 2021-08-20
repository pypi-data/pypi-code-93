from datetime import date
from enum import Enum
from typing import List, Optional

from pandas import DataFrame

from kpler.sdk import Platform
from kpler.sdk.client import KplerClient
from kpler.sdk.configuration import Configuration
from kpler.sdk.helpers import (
    process_date_parameter,
    process_enum_parameters,
    process_list_parameter,
)


class Prices(KplerClient):

    """
    The ``Prices`` endpoint allows you to extract the latest prices information in $/MMBtu for various indexes and prices
    benchmarks, including Henry Hub, TTF, NBP, SLInG (Singapore, N.Asia, DKI), RIM, 11.5% Brent, and 14.5% JCC.
    """

    RESOURCE_NAME = "prices"

    AVAILABLE_PLATFORMS = [Platform.LNG]

    def __init__(self, configuration: Configuration, column_ids: bool = True, log_level=None):
        super().__init__(configuration, self.AVAILABLE_PLATFORMS, column_ids, log_level)

    def get_columns(self) -> DataFrame:
        """
        This endpoint returns a recent and updated list of all columns available for the endpoint prices.

        Examples:
            >>> from kpler.sdk.resources.prices import Prices
            ... prices_client = Prices(config)
            ... prices_client.get_columns()

            .. csv-table::
                :header: "id","name","description","deprecated","type"

                "id","Id","Identifier in the database of Kpler","False","long"
                "index","Index","Name of Index referenced","False","string"
                "ticker","Ticker","None","False","string"
                "reference month","Reference Month","None","False","datetime yyyy-MM-dd HH:mm"
                "date","Date","None","False","datetime yyyy-MM-dd HH:mm"
                "price","Price","None","False","double"
        """

        return self._get_columns_for_resource(self.RESOURCE_NAME)

    def get(
        self,
        size: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        indexes: Optional[List[Enum]] = None,
        columns: Optional[List[str]] = None,
    ):
        """

        Args:
            size: Optional[int] Maximum number of prices returned
            start_date: Optional[date] Start of the period (YYYY-MM-DD)
            end_date: Optional[date] End of the period (YYYY-MM-DD)
            indexes: Optional[List[Enum]] ``PricesIndexes``
            columns: Optional[List[str]] Retrieve all available columns when set to "all"

        Examples:
            >>> from datetime import date
            ... from kpler.sdk.resources.prices import Prices
            ... from kpler.sdk import PricesIndexes
            ... prices_client = Prices(config)
            ... prices_client.get(
            ...     start_date=date(2020,9,1),
            ...     end_date=date(2020,10,1),
            ...     size=10,
            ...     indexes=[PricesIndexes.HenryHub, PricesIndexes.TTF]
            ... )

            .. csv-table::
                :header: "id","index","ticker","reference month","date","price"

                "88530","TTF","TTFN1","2020-11-01 00:00","2020-10-01","4.522"
                "88531","TTF","TTFN2","2020-12-01 00:00","2020-10-01","4.650"
                "88532","TTF","TTFN3","2021-01-01 00:00","2020-10-01","4.711"
                "88533","TTF","TTFN4","2021-02-01 00:00","2020-10-01","4.721"
                "88534","TTF","TTFN5","2021-03-01 00:00","2020-10-01","4.652"
                "88466","Henry Hub","HenryHubN1","2020-10-01 00:00","2020-10-01","2.100"
                "88467","Henry Hub","HenryHubN2","2020-11-01 00:00","2020-10-01","2.564"
                "88468","Henry Hub","HenryHubN3","2020-12-01 00:00","2020-10-01","3.126"
                "88469","Henry Hub","HenryHubN4","2021-01-01 00:00","2020-10-01","3.275"
                "88470","Henry Hub","HenryHubN5","2021-02-01 00:00","2020-10-01","3.223"
        """

        query_parameters = {
            "size": size,
            "startDate": process_date_parameter(start_date),
            "endDate": process_date_parameter(end_date),
            "indexes": process_enum_parameters(indexes),
            "columns": process_list_parameter(columns),
        }
        return self._get_dataframe(self.RESOURCE_NAME, query_parameters)
