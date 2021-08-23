import logging
from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.api.merge_rules.wells import WellMergeRulesAPI
from cognite.well_model.client.models.resource_list import WellList
from cognite.well_model.client.utils.multi_request import cursor_multi_request
from cognite.well_model.models import (
    DateRange,
    ExternalIdItems,
    Filter2,
    LengthRange,
    MeasurementFilters,
    PolygonFilter,
    Search,
    TrajectoryFilter,
    Well,
    WellFilter,
    WellIngestion,
    WellIngestionItems,
    WellItems,
    WellNPTFilter,
)

logger = logging.getLogger(__name__)


class WellsAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)
        self.merge_rules = WellMergeRulesAPI(client)

    def ingest(self, ingestions: List[WellIngestion]) -> List[Well]:
        path = self._get_path("/wells")
        json = WellIngestionItems(items=ingestions).json()
        response: Response = self.client.post(path, json)
        well_items: WellItems = WellItems.parse_obj(response.json())
        items: List[Well] = well_items.items
        return items

    # guranteed to be non-empty list
    def _retrieve_multiple(self, external_ids: List[str]) -> List[Well]:
        self._validate_external_ids(external_ids)
        wells_by_ids = ExternalIdItems(items=external_ids)
        path: str = self._get_path("/wells/byids")
        response: Response = self.client.post(url_path=path, json=wells_by_ids.json())
        wells: List[Well] = WellItems.parse_raw(response.text).items
        return wells

    def retrieve(self, external_id: str) -> Well:
        """
        Get well by external id

        @param external_id: well external id
        @return: Well object
        """
        return self._retrieve_multiple([external_id])[0]

    def retrieve_multiple(self, external_ids: List[str]) -> WellList:
        """
        Get wells by a list of external ids

        @param external_ids: list of well external ids
        @return: list of Well objects
        """
        return WellList(self._retrieve_multiple(external_ids))

    def list(
        self,
        string_matching: Optional[str] = None,
        quadrants: Optional[List[str]] = None,
        blocks: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
        operators: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
        water_depth: Optional[LengthRange] = None,
        spud_date: Optional[DateRange] = None,
        well_types: Optional[List[str]] = None,
        licenses: Optional[List[str]] = None,
        has_trajectory: Optional[TrajectoryFilter] = None,
        has_measurements: Optional[MeasurementFilters] = None,
        npt: Optional[WellNPTFilter] = None,
        polygon: Optional[PolygonFilter] = None,
        output_crs: Optional[str] = None,
        limit=100,
    ) -> WellList:
        """
        Get wells that matches the filter

        @param string_matching - string to fuzzy match on description and name
        @param quadrants - list of quadrants to find wells within
        @param blocks - list of blocks to find wells within
        @param fields - list of fields to find wells within
        @param operators - list of well operators to filter on
        @param sources - list of source system names
        @param water_depth - TODO
        @param spud_date - TODO
        @param licenses - list of well licenses
        @param well_types - list of well types, for example exploration
        @param has_trajectory - filter wells which have trajectory between certain depths
        @param has_measurements - filter wells which have measurements between certain depths in their logs
        @param npt - filter wells on NPT
        @param nds - filter wells on NDS
        @param polygon - geographic area to find wells within
        @param output_crs - crs for the returned well head
        @param limit - number of well objects to fetch
        @return: WellItems object
        """

        def request(cursor):
            search = Search(query=string_matching) if string_matching else None
            well_filter = WellFilter(
                filter=Filter2(
                    quadrants=quadrants,
                    blocks=blocks,
                    fields=fields,
                    operators=operators,
                    well_types=well_types,
                    licenses=licenses,
                    sources=sources,
                    water_depth=water_depth,
                    spud_date=spud_date,
                    has_trajectory=has_trajectory,
                    has_measurements=has_measurements,
                    polygon=polygon,
                    npt=npt,
                ),
                search=search,
                output_crs=output_crs,
                cursor=cursor,
            )
            path: str = self._get_path("/wells/list")
            response: Response = self.client.post(url_path=path, json=well_filter.json())
            well_items_data: WellItems = WellItems.parse_raw(response.text)
            return well_items_data

        items = cursor_multi_request(
            get_cursor=self._get_cursor, get_items=self._get_items, limit=limit, request=request
        )
        return WellList(items)

    @staticmethod
    def _get_items(well_items: WellItems) -> List[Well]:
        items: List[Well] = well_items.items  # For mypy
        return items

    @staticmethod
    def _get_cursor(well_items: WellItems) -> Optional[str]:
        next_cursor: Optional[str] = well_items.next_cursor  # For mypy
        return next_cursor
