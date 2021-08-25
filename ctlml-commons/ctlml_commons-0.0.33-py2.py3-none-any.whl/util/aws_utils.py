from __future__ import annotations

import boto3
from boto3.session import Session

REGION_NAME: str = "us-west-2"

KEY_KEY_MGNR: str = "secretsmanager"


class AwsUtils:
    @classmethod
    def get_resource(cls, name: str = "s3"):
        return boto3.resource(name)

    @classmethod
    def get_client(cls, name: str = KEY_KEY_MGNR, region_name: str = REGION_NAME):
        return AwsUtils.__open_boto_session__().client(service_name=name, region_name=region_name)

    @classmethod
    def __open_boto_session__(cls) -> Session:
        return boto3.session.Session()
