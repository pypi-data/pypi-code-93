from mlplatform_lib.api_client import ApiClient, RunMode
from mlplatform_lib.dataclass.experiment.type import ExperimentType
from mlplatform_lib.dataclass.model.type import ModelStatus
from mlplatform_lib.dataclass.model import ModelPredefinedaiDto, ModelInfoDto
from mlplatform_lib.mlplatform.mlplatform_http_client import MlPlatformUserAuth
from mlplatform_lib.predefinedai.predefinedai_http_client import PredefinedAIHttpClient
import os
from typing import List, Optional


class PredefinedAIApi:
    def __init__(self, api_client: ApiClient = None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

        if api_client.run_mode == RunMode.KUBERNETES:
            self.predefinedai_client = PredefinedAIHttpClient(mlplatform_addr=os.environ["mlplatformAddr"])
            self.mlplatform_auth = MlPlatformUserAuth(
                project_id=self.api_client.projectId,
                user_id=self.api_client.userId,
                authorization=self.api_client.Authorization,
                authorization_type=self.api_client.authorizationType,
            )
        self.experiment_id = self.api_client.experiment_id
        self.train_id = self.api_client.train_id
        self.inference_id = self.api_client.inference_id

    def get_models(self) -> Optional[List[ModelPredefinedaiDto]]:
        if self.api_client.run_mode == RunMode.KUBERNETES:
            return self.predefinedai_client.get_model_infos(
                experiment_id=self.api_client.experiment_id,
                train_id=self.api_client.train_id,
                auth=self.mlplatform_auth,
            )
        else:
            print("Current mode is local, Skip get_model_infos.")
            return None

    def insert_model(self, model: ModelPredefinedaiDto) -> Optional[ModelPredefinedaiDto]:
        if self.api_client.run_mode == RunMode.KUBERNETES:
            model.train_id = self.train_id
            model.status = ModelStatus.SUCCESS
            model.experiment_type = ExperimentType.PREDEFINEDAI
            return self.predefinedai_client.insert_model(
                experiment_id=self.experiment_id,
                train_id=self.train_id,
                model=model,
                auth=self.mlplatform_auth,
            )
        else:
            print("Current mode is local, Skip insert_model_info.")
            model.id = 1
            model.train_id = self.train_id
            model.status = ModelStatus.SUCCESS
            model.experiment_type = ExperimentType.PREDEFINEDAI
            return model

    def insert_model_info(self, model_id: int, model_info: ModelInfoDto) -> ModelInfoDto:
        if self.api_client.run_mode == RunMode.KUBERNETES:
            model_info.status = ModelStatus.SUCCESS
            return self.predefinedai_client.insert_model_info(
                experiment_id=self.experiment_id,
                train_id=self.train_id,
                model_id=model_id,
                model_info=model_info,
                auth=self.mlplatform_auth,
            )
        else:
            print("Current mode is local, Skip insert_visualizations.")

    def upload_inference_csv(self, inference_csv_path: str):
        if self.api_client.run_mode == RunMode.KUBERNETES:
            self.predefinedai_client.upload_inference_csv(
                experiment_id=self.experiment_id,
                inference_id=self.inference_id,
                inference_csv_path=inference_csv_path,
                auth=self.mlplatform_auth,
            )
            os.remove(inference_csv_path)
        else:
            print("Current mode is local, Skip upload_inference_csv.")
