from typing import List, Optional
from urllib.parse import urlencode

from .json_object import JsonObject
from .model import ModelApi
from vectice.entity import ModelVersion
from .Page import Page


class ModelVersionApi(ModelApi):
    def __init__(self, project_token: str, model_id: int, _token: Optional[str] = None):
        super().__init__(project_token=project_token, _token=_token)
        self._model_id = model_id
        self._model_version_path = super().api_base_path + "/" + str(model_id) + "/version"

    @property
    def model_id(self) -> int:
        return self._model_id

    @property
    def api_base_path(self) -> str:
        return self._model_version_path

    def list_model_versions(self, page_index=Page.index, page_size=Page.size) -> List[ModelVersion]:
        queries = {"index": page_index, "size": page_size}
        model_versions = self._get(self.api_base_path + "?" + urlencode(queries))["items"]
        return [ModelVersion(model_version) for model_version in model_versions]

    def create_model_version(self, model_version: JsonObject) -> ModelVersion:
        if model_version.get("status") is None:
            raise ValueError('"status" must be provided in model_version.')
        return ModelVersion(self._post(self.api_base_path, model_version))

    def update_model_version(self, model_id: int, model_version: JsonObject) -> ModelVersion:
        return ModelVersion(self._put(self.api_base_path + "/" + str(model_id), model_version))
