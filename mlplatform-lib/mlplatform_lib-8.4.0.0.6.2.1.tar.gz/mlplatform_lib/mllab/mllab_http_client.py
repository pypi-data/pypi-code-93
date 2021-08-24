from mlplatform_lib.mlplatform.mlplatform_http_client import (
    MlPlatformHttpClient,
    MlPlatformUserAuth,
    MlPlatformRequestType,
)
from mlplatform_lib.dataclass.model.model_dto import ModelDto
from mlplatform_lib.dataclass.inference.inference_dto import InferenceDto
from mlplatform_lib.utils.dataclass_utils import from_dict, to_dict
from typing import List


class MllabHttpClient(MlPlatformHttpClient):
    def __init__(self, mlplatform_addr):
        super().__init__(mlplatform_addr=mlplatform_addr)

    def get_model_list(self, experiment_id: int, auth: MlPlatformUserAuth) -> List[ModelDto]:
        res = self.send_request(
            "models", {"experiments": experiment_id}, {}, {}, auth, MlPlatformRequestType.READ
        )

        model_infos = []
        print(res.data)
        for model_info in res.data:
            model_infos.append(from_dict(ModelDto, model_info))
        return model_infos

    def get_model_by_id(self, experiment_id: int, train_id: int, auth: MlPlatformUserAuth) -> ModelDto:
        res = self.send_request(
            "models",
            {"experiments": experiment_id, "trains": train_id},
            {},
            {},
            auth,
            MlPlatformRequestType.READ,
        )

        model_infos = []
        for model_info in res.data:
            model_infos.append(from_dict(ModelDto, model_info))
        return model_infos[0]

    def update_model(
        self, experiment_id: int, train_id: int, dto: ModelDto, auth: MlPlatformUserAuth
    ) -> dict:
        res = self.send_request(
            "models",
            {"experiments": experiment_id, "trains": train_id},
            {},
            to_dict(dto),
            auth,
            MlPlatformRequestType.UPDATE,
        )
        if res.status_code == 200:
            return True
        else:
            return False

    def get_latest_model(self, experiment_id=int, auth=MlPlatformUserAuth) -> ModelDto:
        res = self.send_request(
            "models",
            {"experiments": experiment_id},
            {"latest": "latest"},
            {},
            auth,
            MlPlatformRequestType.READ,
        )
        return from_dict(ModelDto, res.data[0])

    def get_inference_by_id(
        self, experiment_id: int, inference_id: int, auth: MlPlatformUserAuth
    ) -> InferenceDto:
        res = self.send_request(
            "",
            {"experiments": experiment_id, "inferences": inference_id},
            {},
            {},
            auth,
            MlPlatformRequestType.READ,
        )

        return from_dict(InferenceDto, res.data)

    def update_inference(self, experiment_id: int, dto: InferenceDto, auth: MlPlatformUserAuth) -> dict:
        res = self.send_request(
            "inferences",
            {"experiments": experiment_id},
            {},
            to_dict(dto),
            auth,
            MlPlatformRequestType.UPDATE,
        )
        if res.status_code == 200:
            return True
        else:
            return False
