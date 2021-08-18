import logging
from typing import List

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.models import Source, SourceItems

logger = logging.getLogger(__name__)


class SourcesAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

    def list(self):
        path = self._get_path("/sources")
        response: Response = self.client.get(path)
        source_items: SourceItems = SourceItems.parse_obj(response.json())
        return source_items.items

    def ingest(self, sources: List[Source]) -> List[Source]:
        path = self._get_path("/sources")
        json = SourceItems(items=sources).json()
        response: Response = self.client.post(path, json)
        source_items: SourceItems = SourceItems.parse_obj(response.json())
        return source_items.items
