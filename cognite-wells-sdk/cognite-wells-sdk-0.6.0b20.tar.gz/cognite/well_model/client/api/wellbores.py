import logging
from typing import List

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.api.merge_rules.wellbores import WellboreMergeRulesAPI
from cognite.well_model.client.models.resource_list import WellboreList
from cognite.well_model.models import (
    ExternalIdItems,
    Wellbore,
    WellboreIngestion,
    WellboreIngestionItems,
    WellboreItems,
)

logger = logging.getLogger(__name__)


class WellboresAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)
        self.merge_rules = WellboreMergeRulesAPI(client)

    def ingest(self, ingestions: List[WellboreIngestion]) -> List[Wellbore]:
        path = self._get_path("/wellbores")
        json = WellboreIngestionItems(items=ingestions).json()
        response: Response = self.client.post(path, json)
        wellbore_items: WellboreItems = WellboreItems.parse_obj(response.json())
        wellbores: List[Wellbore] = wellbore_items.items
        return wellbores

    # guranteed to be non-empty list
    def _retrieve_multiple(self, external_ids: List[str]) -> List[Wellbore]:
        self._validate_external_ids(external_ids)
        wellbores_by_ids = ExternalIdItems(items=external_ids)
        path: str = self._get_path("/wellbores/byids")
        response: Response = self.client.post(url_path=path, json=wellbores_by_ids.json())
        wellbore_items: WellboreItems = WellboreItems.parse_raw(response.text)
        wellbores: List[Wellbore] = wellbore_items.items
        return wellbores

    # guranteed to be non-empty list
    def _retrieve_multiple_by_wells(self, well_external_ids: List[str]) -> List[Wellbore]:
        self._validate_external_ids(well_external_ids)
        wells_by_ids = ExternalIdItems(items=well_external_ids)
        path: str = self._get_path("/wellbores/bywellids")
        response: Response = self.client.post(url_path=path, json=wells_by_ids.json())
        wellbore_items: WellboreItems = WellboreItems.parse_raw(response.text)
        wellbores: List[Wellbore] = wellbore_items.items
        return wellbores

    def retrieve(self, external_id: str) -> Wellbore:
        """
        Get wellbore by external id

        @param wellbore_id: wellbore external id
        @return: Wellbore object
        """
        return self._retrieve_multiple([external_id])[0]

    def retrieve_multiple(self, external_ids: List[str]) -> WellboreList:
        """
        Get wellbores by a list of external ids

        @param external_ids: list of wellbore external ids
        @return: list of Wellbore objects
        """
        return WellboreList(self._retrieve_multiple(external_ids))

    def retrieve_multiple_by_well(self, well_external_id: str) -> WellboreList:
        """
        Get wellbores by a well external id

        @param well_external_id: well external id
        @return: list of Wellbore objects
        """
        return WellboreList(self._retrieve_multiple_by_wells([well_external_id]))

    def retrieve_multiple_by_wells(self, well_external_ids: List[str]) -> WellboreList:
        """
        Get wellbores by a list of well external ids

        @param well_external_ids: list of well external ids
        @return: list of Wellbore objects
        """
        return WellboreList(self._retrieve_multiple_by_wells(well_external_ids))
