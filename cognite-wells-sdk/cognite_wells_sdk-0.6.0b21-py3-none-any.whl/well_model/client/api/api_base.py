from typing import List

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.utils.exceptions import CogniteInvalidInput
from cognite.well_model.models import StringItems


class BaseAPI:
    def __init__(self, client: APIClient):
        self.client: APIClient = client

    def _get_path(self, base_url: str) -> str:
        project = self.client._config.project
        return f"/api/playground/projects/{project}/wdl{base_url}"

    def _validate_external_ids(self, external_ids: List[str]):
        if len(external_ids) == 0:
            raise CogniteInvalidInput("list of ids cannot be empty.")

    def _string_items_from_route(self, route: str):
        path: str = self._get_path(f"/{route}")
        response: Response = self.client.get(url_path=path)
        items: StringItems = StringItems.parse_raw(response.text).items
        return items
