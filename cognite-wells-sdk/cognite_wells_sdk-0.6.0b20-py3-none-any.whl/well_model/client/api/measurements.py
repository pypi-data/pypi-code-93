import logging
from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.resource_list import MeasurementDataList, MeasurementList
from cognite.well_model.client.utils.multi_request import cursor_multi_request
from cognite.well_model.models import (
    ExternalIdItems,
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

    def _retrieve_multiple_by_wellbores(self, wellbore_external_ids: List[str]) -> MeasurementList:
        wellbores_by_ids = ExternalIdItems(items=wellbore_external_ids)
        path = self._get_path("/measurements/bywellboreids")
        response: Response = self.client.post(url_path=path, json=wellbores_by_ids.json())
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

    def retrieve_multiple_by_wellbore(self, wellbore_external_id: str) -> MeasurementList:
        """
        Get measurements by a wellbore external id

        @param wellbore_external_id: wellbore external id
        @return: list of SequenceMeasurements objects
        """
        return self._retrieve_multiple_by_wellbores([wellbore_external_id])

    def retrieve_multiple_by_wellbores(self, wellbore_external_ids: List[str]) -> MeasurementList:
        """
        Get measurements by a list of wellbore external ids

        @param wellbore_external_ids: list of wellbore external ids
        @return: list of SequenceMeasurements objects
        """
        return self._retrieve_multiple_by_wellbores(wellbore_external_ids)

    def list_data(self, measurement_data_request_list: List[MeasurementDataRequest]) -> MeasurementDataList:
        """
        Get multiple measurement data by a list of MeasurementDataRequest

        @param measurement_data_request_list: list of MeasurementDataRequest
        @return: list of SequenceGetData objects
        """
        measurement_data_request_items = MeasurementDataRequestItems(items=measurement_data_request_list)
        path = self._get_path("/measurements/data")
        response: Response = self.client.post(url_path=path, json=measurement_data_request_items.json())
        return MeasurementDataList(SequenceDataItems.parse_raw(response.text).items)
