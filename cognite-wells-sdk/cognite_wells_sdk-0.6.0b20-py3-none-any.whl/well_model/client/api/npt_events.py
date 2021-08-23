import logging
from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.resource_list import NPTList
from cognite.well_model.client.utils._identifier_list import identifier_list
from cognite.well_model.client.utils.multi_request import cursor_multi_request
from cognite.well_model.models import (
    NPT,
    DoubleRange,
    Filter,
    Identifier,
    LengthRange,
    NPTFilter,
    NPTIngestion,
    NPTIngestionItems,
    NPTItems,
    StringItems,
)

logger = logging.getLogger(__name__)


class NPTEventsAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

    def ingest(self, npt_events: List[NPTIngestion]):
        """
        Ingests a list of NPT events into WDL

        @param npt_events: list of NPT events to ingest
        @return: list of ingested NPT events
        """
        path = self._get_path("/npt")
        json = NPTIngestionItems(items=npt_events).json()
        response: Response = self.client.post(path, json)
        return NPTList(NPTItems.parse_raw(response.text).items)

    def list(
        self,
        md: Optional[LengthRange] = None,
        duration: Optional[DoubleRange] = None,
        npt_codes: Optional[List[str]] = None,
        npt_code_details: Optional[List[str]] = None,
        wellbore_asset_external_ids: Optional[List[str]] = None,
        wellbore_matching_ids: Optional[List[str]] = None,
        limit: Optional[int] = 100,
    ) -> NPTList:
        """
        Get NPT events that matches the filter

        @param md - range of measured depth in desired NPT events
        @param duration - duration of desired NDS events
        @param npt_codes - npt_codes of desired NDS events
        @param npt_code_details - npt_code_details of desired NDS events
        @param wellbore_external_ids - list of interested wellbore external ids
        @return: NPTList object
        """

        def request(cursor):
            npt_filter = NPTFilter(
                filter=Filter(
                    measured_depth=md,
                    duration=duration,
                    npt_codes=npt_codes,
                    npt_code_details=npt_code_details,
                    wellbore_ids=identifier_list(wellbore_asset_external_ids, wellbore_matching_ids),
                ),
                cursor=cursor,
            )

            path: str = self._get_path("/npt/list")
            response: Response = self.client.post(url_path=path, json=npt_filter.json())
            npt_items: NPTItems = NPTItems.parse_raw(response.text)
            return npt_items

        items = cursor_multi_request(
            get_cursor=self._get_cursor, get_items=self._get_items, limit=limit, request=request
        )
        return NPTList(items)

    def codes(self) -> List[str]:
        """
        Get all NPT codes

        @return: list of NPT codes
        """
        return self._string_items_from_route("npt/codes")

    def detail_codes(self) -> List[str]:
        """
        Get all NPT detail codes

        @return: list of NPT detail codes
        """
        return self._string_items_from_route("npt/detailcodes")

    @staticmethod
    def _get_items(npt_items: NPTItems) -> List[NPT]:
        items: List[NPT] = npt_items.items  # For mypy
        return items

    @staticmethod
    def _get_cursor(npt_items: NPTItems) -> Optional[str]:
        next_cursor: Optional[str] = npt_items.next_cursor  # For mypy
        return next_cursor
