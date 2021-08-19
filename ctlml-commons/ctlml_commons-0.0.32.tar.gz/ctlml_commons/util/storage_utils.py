import pickle
from typing import Any

from ctlml_commons.util.aws_utils import AwsUtils

SERVICE_NAME: str = "s3"

# TODO: move to ctlml_external_accessors
class StorageUtils:
    @classmethod
    def client(cls):
        return AwsUtils.get_resource(name=SERVICE_NAME)

    @classmethod
    def get_bucket(cls, bucket_name: str):
        return cls.client().Bucket(bucket_name)

    @classmethod
    def get(cls, bucket_name: str, path: str):
        print(f"getting to {bucket_name}...path: {path}")
        return pickle.loads(cls.client().Object(bucket_name, path).get()["Body"].read())

    @classmethod
    def upload(cls, bucket_name: str, path: str, data: Any) -> None:
        print(f"putting to {bucket_name}...path: {path}")
        StorageUtils.get_bucket(bucket_name=bucket_name).put_object(Key=path, Body=pickle.dumps(data))
