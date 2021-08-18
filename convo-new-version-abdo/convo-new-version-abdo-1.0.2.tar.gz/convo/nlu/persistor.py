import logging
import os
import shutil
import tarfile
from typing import List, Optional, Text, Tuple

import convo.shared.utils.common
import convo.utils.common


log = logging.getLogger(__name__)


def fetch_persistor(name: Text) -> Optional["Persevere"]:
    """Returns an instance of the requested persistor.

    Currently, `aws`, `gcs`, `azure` and providing module convo_paths are supported remote storages."""

    if name == "aws":
        return PersistorAWS(
            os.environ.get("BUCKET_NAME"), os.environ.get("AWS_ENDPOINT_URL")
        )
    if name == "gcs":
        return PersistorGCS(os.environ.get("BUCKET_NAME"))

    if name == "azure":
        return PersistorAzure(
            os.environ.get("AZURE_CONTAINER"),
            os.environ.get("AZURE_ACCOUNT_NAME"),
            os.environ.get("AZURE_ACCOUNT_KEY"),
        )
    if name:
        try:
            persevere = convo.shared.utils.common.class_name_from_module_path(name)
            return persevere()
        except ImportError:
            raise ImportError(
                f"Unknown model persistor {name}. Please make sure to "
                "either use an included model persistor (`aws`, `gcs` "
                "or `azure`) or specify the module path to an external "
                "model persistor."
            )
    return None


class Persevere:
    """Store models in cloud and fetch them when needed"""

    def persist(self, model_directory: Text, model_name: Text) -> None:
        """Uploads a model persisted in the `target_dir` to cloud storage."""

        if not os.path.isdir(model_directory):
            raise ValueError(f"Target dir '{model_directory}' not found.")

        key_of_file, path_of_tar = self._compression(model_directory, model_name)
        self._tar_persistance(key_of_file, path_of_tar)

    def retrieval(self, model_name: Text, target_path: Text) -> None:
        """Downloads a model that has been persisted to cloud storage."""

        name_of_tar = model_name

        if not model_name.endswith("tar.gz"):
            # ensure backward compatibility
            name_of_tar = self._name_tar(model_name)

        self._tar_retrieval(name_of_tar)
        self._de_compress(os.path.basename(name_of_tar), target_path)

    def models_list(self) -> List[Text]:
        """Lists all the trained models."""

        raise NotImplementedError

    def _tar_retrieval(self, filename: Text) -> Text:
        """Downloads a model previously persisted to cloud storage."""

        raise NotImplementedError("")

    def _tar_persistance(self, filekey: Text, tarname: Text) -> None:
        """Uploads a model persisted in the `target_dir` to cloud storage."""

        raise NotImplementedError("")

    def _compression(self, model_directory: Text, model_name: Text) -> Tuple[Text, Text]:
        """Creates a compressed archive and returns key and tar."""
        import tempfile

        directory_path = tempfile.mkdtemp()
        root_name = self._name_tar(model_name, include_extension=False)
        tar_name = shutil.make_archive(
            os.path.join(directory_path, root_name),
            "gztar",
            root_dir=model_directory,
            base_dir=".",
        )
        file_key_name = os.path.basename(tar_name)
        return file_key_name, tar_name

    @staticmethod
    def _model_directory_and_model_from_file_name(filename: Text) -> Tuple[Text, Text]:

        split = filename.split("___")
        if len(split) > 1:
            name_of_model = split[1].replace(".tar.gz", "")
            return split[0], name_of_model
        else:
            return split[0], ""

    @staticmethod
    def _name_tar(model_name: Text, include_extension: bool = True) -> Text:

        extra = ".tar.gz" if include_extension else ""
        return f"{model_name}{extra}"

    @staticmethod
    def _de_compress(compressed_path: Text, target_path: Text) -> None:

        with tarfile.open(compressed_path, "r:gz") as tar:
            tar.extractall(target_path)  # target dir will be created if it not exists


class PersistorAWS(Persevere):
    """Store models on S3.

    Fetches them when needed, instead of storing them on the local disk."""

    def __init__(
        self,
        bucket_name: Text,
        endpoint_url: Optional[Text] = None,
        region_name: Optional[Text] = None,
    ) -> None:
        import boto3

        super().__init__()
        self.s3 = boto3.resource(
            "s3", endpoint_url=endpoint_url, region_name=region_name
        )
        self._bucket_exists_check(bucket_name, region_name)
        self.bucket_name = bucket_name
        self.bucket = self.s3.Bucket(bucket_name)

    def models_list(self) -> List[Text]:
        try:
            return [
                self._model_directory_and_model_from_file_name(obj.key)[1]
                for obj in self.bucket.objects.filter()
            ]
        except Exception as e:
            log.warning(f"Failed to list models in AWS. {e}")
            return []

    def _bucket_exists_check(
        self, bucket_name: Text, name_of_region: Optional[Text] = None
    ) -> None:
        import boto3
        import botocore

        if not name_of_region:
            name_of_region = boto3.DEFAULT_SESSION.region_name

        bucket_configuration = {"LocationConstraint": name_of_region}
        # noinspection PyUnresolvedReferences
        try:
            self.s3.create_bucket(
                Bucket=bucket_name, CreateBucketConfiguration=bucket_configuration
            )
        except botocore.exceptions.ClientError:
            pass  # bucket already exists

    def _tar_persistance(self, file_key: Text, tar_path: Text) -> None:
        """Uploads a model persisted in the `target_dir` to s3."""

        with open(tar_path, "rb") as f:
            self.s3.Object(self.bucket_name, file_key).put(Body=f)

    def _tar_retrieval(self, model_path: Text) -> None:
        """Downloads a model that has previously been persisted to s3."""
        name_of_tar = os.path.basename(model_path)
        with open(name_of_tar, "wb") as f:
            self.bucket.download_fileobj(model_path, f)


class PersistorGCS(Persevere):
    """Store models on Google Cloud Storage.

    Fetches them when needed, instead of storing them on the local disk."""

    def __init__(self, bucket_name: Text) -> None:
        from google.cloud import storage

        super().__init__()

        self.storage_client = storage.Client()
        self._bucket_exists_check(bucket_name)

        self.bucket_name = bucket_name
        self.bucket = self.storage_client.bucket(bucket_name)

    def models_list(self) -> List[Text]:

        try:
            iterating_blob = self.bucket.list_blobs()
            return [
                self._model_directory_and_model_from_file_name(b.name)[1]
                for b in iterating_blob
            ]
        except Exception as e:
            log.warning(f"Failed to list models in google cloud storage. {e}")
            return []

    def _bucket_exists_check(self, bucket_name: Text) -> None:
        from google.cloud import exceptions

        try:
            self.storage_client.create_bucket(bucket_name)
        except exceptions.Conflict:
            # bucket exists
            pass

    def _tar_persistance(self, file_key: Text, tar_path: Text) -> None:
        """Uploads a model persisted in the `target_dir` to GCS."""

        drop = self.bucket.blob(file_key)
        drop.upload_from_filename(tar_path)

    def _tar_retrieval(self, target_filename: Text) -> None:
        """Downloads a model that has previously been persisted to GCS."""

        blob = self.bucket.blob(target_filename)
        blob.download_to_filename(target_filename)


class PersistorAzure(Persevere):
    """Store models on Azure"""

    def __init__(
        self, azure_container: Text, azure_account_name: Text, azure_account_key: Text
    ) -> None:
        from azure.storage.blob import BlobServiceClient

        super().__init__()

        self.blob_service = BlobServiceClient(
            account_url=f"https://{azure_account_name}.blob.core.windows.net/",
            credential=azure_account_key,
        )

        self._confirm_container_exists(azure_container)
        self.container_name = azure_container

    def _confirm_container_exists(self, container_name: Text) -> None:
        from azure.core.exceptions import ResourceExistsError

        try:
            self.blob_service.create_container(container_name)
        except ResourceExistsError:
            # no need to create the container, it already exists
            pass

    def _container_exists_check(self):
        return self.blob_service.get_container_client(self.container_name)

    def models_list(self) -> List[Text]:

        try:
            iterating_blob = self._container_exists_check().list_blobs()
            return [
                self._model_directory_and_model_from_file_name(b.name)[1]
                for b in iterating_blob
            ]
        except Exception as e:
            log.warning(f"Failed to list models azure blob storage. {e}")
            return []

    def _tar_persistance(self, file_key: Text, tar_path: Text) -> None:
        """Uploads a model persisted in the `target_dir` to Azure."""

        with open(tar_path, "rb") as data:
            self._container_exists_check().upload_blob(name=file_key, data=data)

    def _tar_retrieval(self, target_filename: Text) -> None:
        """Downloads a model that has previously been persisted to Azure."""

        client_blob = self._container_exists_check().get_blob_client(target_filename)

        with open(target_filename, "wb") as blob:
            stream_download = client_blob.download_blob()
            blob.write(stream_download.readall())
