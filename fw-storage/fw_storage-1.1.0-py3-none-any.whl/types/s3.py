"""S3 storage module."""
import re
import typing as t
from contextlib import contextmanager
from functools import partial

import boto3
import boto3.s3.transfer
import botocore.client
import botocore.config
import botocore.exceptions

from ..fileinfo import FileInfo
from ..filters import Filters, create_filter
from ..storage import AnyPath, CloudStorage, FileNotFound, PermError, StorageError

__all__ = ["S3"]

CHUNKSIZE = 8 << 20
TRANSFER_CONFIG = boto3.s3.transfer.TransferConfig(
    multipart_chunksize=CHUNKSIZE, io_chunksize=CHUNKSIZE
)


def create_default_client(
    access_key: t.Optional[str] = None, secret_access_key: t.Optional[str] = None
) -> botocore.client.BaseClient:
    """Create S3 boto client.

    See how boto determines credentials:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
    """
    session = boto3.session.Session(
        aws_access_key_id=access_key, aws_secret_access_key=secret_access_key
    )
    return session.client(
        "s3",
        config=botocore.config.Config(
            signature_version="s3v4",
            retries={"max_attempts": 3},
        ),
    )


@contextmanager
def translate_error(context: str):
    """Translate botocore's ClientError to StorageError."""
    try:
        yield
    except botocore.exceptions.ClientError as exc:
        status_code = exc.response["ResponseMetadata"]["HTTPStatusCode"]
        if status_code not in (403, 404):
            raise
        err_cls = FileNotFound if status_code == 404 else PermError
        msg = f"{exc.response['Error']['Message']} {context!r}"
        raise err_cls(msg) from exc


class S3(CloudStorage):
    """Storage class for Amazon S3 object storage."""

    url_re = re.compile(
        r"s3://(?P<bucket>[^:/?#]+)((?P<prefix>/[^?#]+))?(\?(?P<query>[^#]+))?"
    )

    def __init__(
        self,
        bucket: str,
        *,
        prefix: str = "",
        access_key_id: t.Optional[str] = None,
        secret_access_key: t.Optional[str] = None,
        create_client: t.Callable = create_default_client,
        **kwargs: t.Any,
    ):
        """S3 storage class listing/reading/writing files from an S3 bucket.

        Args:
            bucket (str): S3 bucket name.
            prefix (str): Root prefix. Default: "".
            access_key_id (str, optional): Access key id.
            secret_access_key (str, optional): Secret access key.
            create_client (callable): Callable to create the S3 client.
                Default: create_default_client.
            write (bool): Pre-check that bucket is writable. Default: False.
        """
        self.bucket = bucket
        self.prefix = prefix.strip("/")
        self.client = create_client(
            access_key=access_key_id, secret_access_key=secret_access_key
        )
        super().__init__(**kwargs)

    def abspath(self, path: AnyPath) -> str:
        """Return absolute path for a given path."""
        return f"{self.prefix}/{self.relpath(path)}".lstrip("/")

    def check_access(self):
        """Check bucket is accessible."""
        with translate_error(self.bucket):
            self.client.head_bucket(Bucket=self.bucket)

    def ls(
        self, path: str = "", *, include: Filters = None, exclude: Filters = None, **_
    ) -> t.Iterator[FileInfo]:
        """Yield each item under prefix matching the include/exclude filters."""
        filt = create_filter(include=include, exclude=exclude)
        paginator = self.client.get_paginator("list_objects_v2")
        prefix = f"{self.prefix}/{path}".rstrip("/")
        pages = paginator.paginate(Bucket=self.bucket, Prefix=prefix)
        for page in pages:
            for content in page.get("Contents", []):
                filepath: str = content["Key"]
                relpath = re.sub(fr"^{self.prefix}", "", filepath).lstrip("/")
                info = FileInfo(
                    path=relpath,
                    size=content["Size"],
                    created=content["LastModified"].timestamp(),  # TODO consider None
                    modified=content["LastModified"].timestamp(),
                )
                if filt.match(info):
                    yield info

    def stat(self, path: str) -> FileInfo:
        """Return FileInfo for a single file."""
        key = f"{self.prefix}/{path}".lstrip("/")
        with translate_error(f"{self.bucket}/{path}"):
            meta = self.client.head_object(Bucket=self.bucket, Key=key)
        return FileInfo(
            path=path,
            size=meta["ContentLength"],
            created=meta["LastModified"].timestamp(),  # TODO consider None
            modified=meta["LastModified"].timestamp(),
        )

    def download_file(self, path: str, dst: t.IO[bytes]) -> None:
        """Download file and it opened for reading in binary mode."""
        bucket = self.bucket
        with translate_error(f"{bucket}/{path}"):
            self.client.download_fileobj(bucket, path, dst, Config=TRANSFER_CONFIG)

    def upload_file(self, path: str, file: t.Union[str, bytes, t.IO[bytes]]) -> None:
        """Upload file to the given path."""
        if isinstance(file, bytes):
            upload = partial(self.client.put_object, Body=file)
        elif isinstance(file, str):
            upload = partial(self.client.upload_file, file, Config=TRANSFER_CONFIG)
        else:
            upload = partial(self.client.upload_fileobj, file, Config=TRANSFER_CONFIG)
        with translate_error(f"{self.bucket}/{path}"):
            upload(Bucket=self.bucket, Key=path)

    def flush_delete(self):
        """Flush pending remove operations."""
        keys = sorted(self.delete_keys)
        objects = {"Objects": [{"Key": key} for key in keys], "Quiet": True}
        with translate_error("Bulk delete operation"):
            resp = self.client.delete_objects(Bucket=self.bucket, Delete=objects)
        self.delete_keys.difference_update(self.delete_keys)
        if len(resp.get("Errors", [])) > 0:
            msg = f"Bulk delete operation failed for {len(resp['Errors'])} files"
            prefix = f"{self.bucket}/{self.prefix}"
            errors = [f"{prefix}/{e['Key']}: {e['Message']}" for e in resp["Errors"]]
            raise StorageError(msg, errors=errors)
