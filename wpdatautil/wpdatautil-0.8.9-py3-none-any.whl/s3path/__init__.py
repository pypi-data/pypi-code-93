"""s3path utilities."""
import logging
import shutil
from pathlib import Path
from typing import Union

from s3path import S3Path

from wpdatautil.pathlib import path_to_uri

AnyPath = Union[Path, S3Path]

log = logging.getLogger(__name__)


def rmdirtree(path: AnyPath) -> None:
    """Remove the local or S3 path."""
    uri = path_to_uri(path)

    if not path.exists():
        log.info(f"Path {uri} does not exist.")
        return

    log.info(f"Removing path {uri}.")
    if isinstance(path, S3Path):
        path.rmdir()
    else:
        shutil.rmtree(path, ignore_errors=True)
    assert list(path.rglob("*")) == []
    log.info(f"Removed path {uri}.")
