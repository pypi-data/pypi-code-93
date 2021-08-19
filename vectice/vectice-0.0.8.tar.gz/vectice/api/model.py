from typing import List, Optional
from urllib.parse import urlencode

from vectice.api.project import ProjectApi
from vectice.entity import Model
from .json_object import JsonObject
from .Page import Page


class ModelApi(ProjectApi):
    def __init__(self, project_token: str, _token: Optional[str] = None):
        super().__init__(project_token=project_token, _token=_token)
        self._model_path = super().api_base_path + "/model"

    @property
    def api_base_path(self) -> str:
        return self._model_path

    def list_models(self, search: str = None, page_index=Page.index, page_size=Page.size) -> List[Model]:
        queries = {"index": page_index, "size": page_size}
        if search:
            queries["search"] = search
        models = self._get(self.api_base_path + "?" + urlencode(queries))["items"]
        return [Model(model) for model in models]

    def create_model(self, model: JsonObject) -> Model:
        if model.get("name") is None:
            raise ValueError('"name" must be provided in model.')
        if model.get("type") is None:
            model["type"] = "OTHER"
        return Model(self._post(self.api_base_path, model))

    def update_model(self, model_id: int, model: JsonObject) -> Model:
        return Model(self._put(self.api_base_path + "/" + str(model_id), model))
