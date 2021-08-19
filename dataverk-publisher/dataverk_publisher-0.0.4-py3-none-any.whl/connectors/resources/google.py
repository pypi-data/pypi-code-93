from google.cloud import storage
from google.cloud import exceptions as gcloud_exceptions
from dataverk_publisher.connectors.resources.base import StorageBase


class GoogleStorageConnector(StorageBase):
    def __init__(self, bucket_name: str):
        super().__init__()
        self.bucket = self._get_bucket_connection(bucket_name)

    def write(self, file, dp_id: str, resource_path: str, fmt: str, **kwargs):
        try:
            name = f"{dp_id}/{resource_path}"
            blob = self.bucket.blob(name)
            blob.upload_from_string(file)
        except gcloud_exceptions.GoogleCloudError as error:
            self.logger.error(f"Error writing file {name} to google storage: {error}")
            raise
        else:
            self.logger.info(f"{name} successfully written to {blob.public_url}")
            return {"id": dp_id, "status": f"{blob.public_url} uploaded"}

    def _get_bucket_connection(self, bucket_name):
        try:
            storage_client = storage.Client()
            return self._get_bucket(storage_client, bucket_name)
        except gcloud_exceptions.GoogleCloudError as error:
            self.logger.error(f"Unable to get bucket {bucket_name}: {error}")
            raise

    @staticmethod
    def _get_bucket(storage_client, bucket_name):
        try:
            return storage_client.get_bucket(bucket_name)
        except gcloud_exceptions.NotFound:
            raise
