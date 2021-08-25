import logging
from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.resource_list import MeasurementDataList, MeasurementList
from cognite.well_model.client.models.sequence_rows import SequenceRows
from cognite.well_model.client.utils._identifier_list import identifier_items, identifier_items_single
from cognite.well_model.models import (
    IdentifierItems,
    MeasurementDataRequest,
    MeasurementDataRequestItems,
    MeasurementIngestionItems,
    MeasurementItems,
    SequenceDataItems,
    SequenceMeasurements,
)

logger = logging.getLogger(__name__)


class MeasurementsAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

    def _retrieve_multiple_by_wellbores(self, identifiers: IdentifierItems) -> MeasurementList:
        path = self._get_path("/measurements/bywellboreids")
        response: Response = self.client.post(url_path=path, json=identifiers.json())
        return MeasurementList(MeasurementItems.parse_raw(response.text).items)

    def ingest(self, measurements: List[SequenceMeasurements]) -> MeasurementList:
        """
        Ingests a list of measurements into WDL

        @param measurements: list of measurements to ingest
        @return: list of ingested measurements
        """
        path = self._get_path("/measurements")
        json = MeasurementIngestionItems(items=measurements).json()
        response: Response = self.client.post(path, json)
        return MeasurementList(MeasurementItems.parse_raw(response.text).items)

    def retrieve_multiple_by_wellbore(
        self, asset_external_id: Optional[str] = None, matching_id: Optional[str] = None
    ) -> MeasurementList:
        """
        Get measurements by asset external id or matching id.

        @param asset_external_id: Wellbore asset external id
        @param matching_id: Wellbore matching id
        @return: list of SequenceMeasurements objects
        """
        identifiers = identifier_items_single(asset_external_id, matching_id)
        return self._retrieve_multiple_by_wellbores(identifiers)

    def retrieve_multiple_by_wellbores(
        self, asset_external_ids: Optional[List[str]] = None, matching_ids: Optional[List[str]] = None
    ) -> MeasurementList:
        """
        Get measurements by a list of asset external ids and matching ids

        @param asset_external_ids: list of wellbore asset external ids
        @param matching_ids: List of wellbore matching ids

        @return: list of SequenceMeasurements objects
        """
        identifiers = identifier_items(asset_external_ids, matching_ids)
        return self._retrieve_multiple_by_wellbores(identifiers)

    def list_data(self, measurement_data_request_list: List[MeasurementDataRequest]) -> MeasurementDataList:
        """
        Get multiple measurement data by a list of MeasurementDataRequest

        @param measurement_data_request_list: list of MeasurementDataRequest
        @return: list of SequenceGetData objects
        """
        measurement_data_request_items = MeasurementDataRequestItems(items=measurement_data_request_list)
        path = self._get_path("/measurements/data")
        response: Response = self.client.post(url_path=path, json=measurement_data_request_items.json())
        items = SequenceDataItems.parse_raw(response.text).items
        items = [SequenceRows.from_sequence_data(x) for x in items]
        return MeasurementDataList(items)
