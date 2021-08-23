import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import boto3
from asbool import asbool
from botocore.config import Config
from loguru import logger

from snatch.helpers.merge_dicts import merge_dicts


@dataclass
class SecretManager:
    current_environment: str
    project_name: str
    current_env_data: Dict[Any, Any]
    _client: Optional[boto3.client] = None

    @property
    def can_read_secrets(self) -> bool:
        return (
            asbool(os.getenv("SNATCH_READ_SECRETS_DATA"))
            if os.getenv("SNATCH_READ_SECRETS_DATA")
            else True
        )

    @property
    def client(self) -> boto3.client:
        if self._client:
            return self._client

        region_name = os.getenv("AWS_REGION", "us-east-1")
        if not os.getenv("AWS_ACCESS_KEY_ID_SHARED", None):
            # just initialize, will check for `.aws/credentials` file
            self._client = boto3.client("secretsmanager", region_name=region_name)
            return self._client

        aws_config = Config(region_name=region_name)
        client_config = {
            "config": aws_config,
            "aws_access_key_id": os.environ["AWS_ACCESS_KEY_ID_SHARED"],
            "aws_secret_access_key": os.environ["AWS_SECRET_ACCESS_KEY_SHARED"],
        }
        aws_session_token = os.getenv("AWS_SESSION_TOKEN_SHARED")

        if aws_session_token:
            client_config["aws_session_token"] = aws_session_token

        self._client = boto3.client("secretsmanager", **client_config)
        return self._client

    def _get_available_secrets(self) -> List[str]:
        all_secrets = self.client.list_secrets(
            MaxResults=100,
            Filters=[
                {
                    "Key": "name",
                    "Values": [
                        "/datasource/local/snatch",
                        "/datasource/dev/snatch",
                        "/datasource/staging/snatch",
                        "/datasource/production/snatch",
                        "/datasource/stg/snatch",
                        "/datasource/prd/snatch",
                    ],
                },
            ],
        )
        all_keys = [
            secret["Name"]
            for secret in all_secrets["SecretList"]
            if f"{self.current_environment}/snatch" in secret["Name"]
        ]
        logger.debug(f"All Keys found: {all_keys}")
        project_keys = [
            secret
            for secret in all_keys
            if f"{self.current_environment}/snatch" in secret
        ]
        logger.debug(f"Project Keys found: {project_keys}")
        return project_keys

    def get_project_secrets(self) -> Dict[Any, Any]:
        secrets_manager_data = {}
        needed_secrets = self._get_available_secrets()
        for secret in needed_secrets:
            logger.debug(f"Reading Secret: {secret} ...")
            secret_name = secret.split("/")[-1]
            secret_data = {secret_name: None}
            response = self.client.get_secret_value(SecretId=secret)
            data = json.loads(response["SecretString"])
            secret_data[secret_name] = {
                key.lower().strip(): data[key] for key in data.keys()
            }
            merge_dicts(secret_data, secrets_manager_data)
        return secrets_manager_data
