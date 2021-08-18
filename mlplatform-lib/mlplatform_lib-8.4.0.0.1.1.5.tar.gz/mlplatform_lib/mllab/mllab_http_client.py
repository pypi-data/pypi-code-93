from mlplatform_lib.mlplatform.mlplatform_http_client import (
    MlPlatformHttpClient,
    MlPlatformUserAuth,
    MlPlatformRequestType,
)
from mlplatform_lib.dataclass.model.model_dto import ModelDto
from typing import List

class MllabHttpClient(MlPlatformHttpClient):
    def __init__(self, mlplatform_addr):
        super().__init__(mlplatform_addr=mlplatform_addr)

    def get_model_list(
        self,
        experiment_id: int,
        auth: MlPlatformUserAuth
    ) -> List[ModelDto]:
        res = self.send_request(
            "models",
            {"experiments": experiment_id},
            {},
            {},
            auth,
            MlPlatformRequestType.READ
        )

        model_infos = []
        for model_info in res.data:
            model_infos.append(ModelDto.from_dict(model_info))
        return model_infos
        
    def get_model_by_id(
        self,
        experiment_id: int,
        train_id: int,
        auth: MlPlatformUserAuth
    ) -> ModelDto:
        res = self.send_request(
            "models",
            {"experiments": experiment_id, "trains": train_id},
            {},
            {},
            auth,
            MlPlatformRequestType.READ
        )

        model_infos = []
        for model_info in res.data:
            model_infos.append(ModelDto.from_dict(model_info))
        return model_infos

    def update_model(
        self,
        experiment_id: int,
        train_id: int,
        dto: ModelDto,
        auth: MlPlatformUserAuth
    ) -> dict:
        res = self.send_request(
            "models",
            {"experiments" : experiment_id, "trains" : train_id},
            {},
            dto.to_dict(),
            auth,
            MlPlatformRequestType.UPDATE
        )
        if res.status_code == 200:
            return True
        else :
            return False
    
    def get_latest_model_id(
        self,
        experiment_id = int,
        auth = MlPlatformUserAuth
    ) -> ModelDto:
        res = self.send_request(
            "models",
            {"experiments" : experiment_id},
            {"latest":"latest"},
            {},
            auth,
            MlPlatformRequestType.READ
        )
        return ModelDto.from_dict(res.data)
        


    
