import logging
from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.resource_list import TrajectoryDataList, TrajectoryList
from cognite.well_model.client.models.trajectory_rows import TrajectoryRows
from cognite.well_model.client.utils._identifier_list import identifier_items, identifier_items_single
from cognite.well_model.models import (
    IdentifierItems,
    Trajectory,
    TrajectoryDataItems,
    TrajectoryDataRequest,
    TrajectoryDataRequestItems,
    TrajectoryIngestion,
    TrajectoryIngestionItems,
    TrajectoryItems,
)

logger = logging.getLogger(__name__)


class TrajectoriesAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

    def _retrieve_multiple_by_wellbores(self, identifiers: IdentifierItems) -> TrajectoryList:
        path = self._get_path("/trajectories/bywellboreids")
        response: Response = self.client.post(url_path=path, json=identifiers.json())
        return TrajectoryList(TrajectoryItems.parse_raw(response.text).items)

    def retrieve_multiple_by_wellbore(
        self, asset_external_id: Optional[str] = None, matching_id: Optional[str] = None
    ) -> TrajectoryList:
        """
        Get trajectories by a wellbore asset external id or matching id

        @param asset_external_id: Wellbore asset external id
        @param matching_id: Wellbore matching id
        @return: list of Trajectory objects
        """
        identifiers = identifier_items_single(asset_external_id, matching_id)
        return self._retrieve_multiple_by_wellbores(identifiers)

    def retrieve_multiple_by_wellbores(
        self, asset_external_ids: Optional[List[str]] = None, matching_ids: Optional[List[str]] = None
    ) -> TrajectoryList:
        """
        Get trajectories by a list of wellbore asset external ids and matching ids

        @param asset_external_ids: list of wellbore asset external ids
        @param matching_ids: List of wellbore matching ids
        @return: list of Trajectory objects
        """
        identifiers = identifier_items(asset_external_ids, matching_ids)
        return self._retrieve_multiple_by_wellbores(identifiers)

    def list_data(self, trajectory_data_request_list: List[TrajectoryDataRequest]) -> TrajectoryDataList:
        """
        Get multiple trajectory data by a list of TrajectoryDataRequest

        @param trajectory_data_request_list: list of trajectory data requests
        @return: list of TrajectoryData objects
        """
        trajectory_data_request_items = TrajectoryDataRequestItems(items=trajectory_data_request_list)
        path = self._get_path("/trajectories/data")
        response: Response = self.client.post(url_path=path, json=trajectory_data_request_items.json())
        trajectory_data_items = TrajectoryDataItems.parse_raw(response.text)
        trajectory_rows = [TrajectoryRows(x) for x in trajectory_data_items.items]
        return TrajectoryDataList(trajectory_rows)

    def ingest(self, ingestions: List[TrajectoryIngestion]) -> List[Trajectory]:
        """
        Ingests list of trajectories into WDL

        @param ingestions: list of trajectories to ingest
        @return: list of ingested trajectories
        """
        path = self._get_path("/trajectories")
        json = TrajectoryIngestionItems(items=ingestions).json()
        response: Response = self.client.post(path, json)

        return [Trajectory.parse_obj(x) for x in response.json()["items"]]
