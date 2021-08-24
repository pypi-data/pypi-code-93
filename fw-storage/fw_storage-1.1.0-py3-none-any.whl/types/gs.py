"""Google Cloud Storage module."""
import json
import os
import pathlib
import re
import typing as t
from contextlib import contextmanager

import google.api_core.exceptions
from google.cloud.storage import Client
from google.oauth2.service_account import Credentials

from ..fileinfo import FileInfo
from ..filters import Filters, create_filter
from ..storage import AnyPath, CloudStorage, FileNotFound, PermError


def create_default_client(key: t.Optional[str] = None):
    """Get default storage client.

    See how google auth determines credentials:
    https://google-auth.readthedocs.io/en/latest/reference/google.auth.html
    """
    key = key or os.getenv("GS_SERVICE_ACCOUNT_KEY", "")
    if not key:
        # let google sdk to get default credentials
        return Client()
    try:
        creds_info = json.loads(key)
    except json.JSONDecodeError:
        creds_info = json.loads(pathlib.Path(key).read_text())
    credentials = Credentials.from_service_account_info(creds_info)
    return Client(credentials=credentials)


@contextmanager
def translate_error(context: str):
    """Translate Google HTTP error to StorageError."""
    try:
        yield
    except google.api_core.exceptions.NotFound as exc:
        raise FileNotFound(f"Not found: {context}") from exc
    except google.api_core.exceptions.Forbidden as exc:
        raise PermError(f"Permission denied: {context}") from exc


class GoogleCloudStorage(CloudStorage):
    """Storage class for Google Cloud Storage."""

    url_re = re.compile(
        r"gs://(?P<bucket>[^:/?#]+)((?P<prefix>/[^?#]+))?(\?(?P<query>[^#]+))?"
    )

    def __init__(
        self,
        bucket: str,
        *,
        prefix: str = "",
        service_account_key: t.Optional[str] = None,
        create_client: t.Callable = create_default_client,
        **kwargs: t.Any,
    ):
        """GS storage class listing/reading/writing files from a Google Storage bucket.

        Args:
            bucket (str): S3 bucket name.
            prefix (str): Root prefix. Default: "".
            service_account_key (str): Key file or key file content as a string.
            create_client (callable): Callable to create the S3 client.
                Default: create_default_client.
            write (bool): Pre-check that bucket is writable. Default: False.
        """
        self.bucket = bucket
        self.prefix = prefix.strip("/")
        self.client = create_client(key=service_account_key)
        super().__init__(**kwargs)

    def abspath(self, path: AnyPath) -> str:
        """Return absolute path for a given path."""
        return f"{self.prefix}/{self.relpath(path)}".lstrip("/")

    def check_access(self):
        """Check bucket is accessible."""
        with translate_error(self.bucket):
            if not self.client.bucket(self.bucket).exists():
                raise FileNotFound(f"Bucket not found: {self.bucket!r}")

    def ls(
        self, path: str = "", *, include: Filters = None, exclude: Filters = None, **_
    ) -> t.Iterator[FileInfo]:
        """Yield each item under prefix matching the include/exclude filters."""
        filt = create_filter(include=include, exclude=exclude)
        prefix = f"{self.prefix}/{path}".rstrip("/")
        for blob in self.client.list_blobs(self.bucket, prefix=prefix):
            relpath = re.sub(fr"^{self.prefix}", "", blob.name).lstrip("/")
            info = FileInfo(
                path=relpath,
                size=blob.size,
                created=blob.time_created.timestamp(),
                modified=blob.updated.timestamp(),
            )
            if filt.match(info):
                yield info

    def stat(self, path: str) -> FileInfo:
        """Return FileInfo for a single file."""
        key = f"{self.prefix}/{path}".lstrip("/")
        with translate_error(f"{self.bucket}/{path}"):
            blob = self.client.bucket(self.bucket).blob(key)
            blob.reload()
        return FileInfo(
            path=path,
            size=blob.size,
            created=blob.time_created.timestamp(),
            modified=blob.updated.timestamp(),
        )

    def download_file(self, path: str, dst: t.IO[bytes]) -> None:
        """Download file and it opened for reading in binary mode."""
        with translate_error(f"{self.bucket}/{path}"):
            self.client.bucket(self.bucket).blob(path).download_to_file(dst)

    def upload_file(self, path: str, file: t.Union[str, bytes, t.IO[bytes]]) -> None:
        """Upload file to the given path."""
        blob = self.client.bucket(self.bucket).blob(path)
        if isinstance(file, bytes):
            upload_func = blob.upload_from_string
        elif isinstance(file, str):
            upload_func = blob.upload_from_filename
        else:
            upload_func = blob.upload_from_file
        with translate_error(path):
            upload_func(file)

    def flush_delete(self):
        """Flush pending remove operations."""
        with translate_error("Bulk delete operation"), self.client.batch():
            for key in sorted(self.delete_keys):
                self.client.bucket(self.bucket).blob(key).delete()
                self.delete_keys.remove(key)
