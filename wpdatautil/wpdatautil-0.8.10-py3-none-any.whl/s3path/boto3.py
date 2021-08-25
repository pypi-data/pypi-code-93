"""s3path boto3 utilities."""
import concurrent.futures
import logging
import os
import shutil
from pathlib import Path
from typing import Dict, Optional, Union

import boto3
from s3path import S3Path

from wpdatautil.pathlib import path_to_uri
from wpdatautil.timeit import Timer

AnyPath = Union[Path, S3Path]

log = logging.getLogger(__name__)


def cp_file(input_path: AnyPath, output_path: AnyPath, *, boto3_kwargs: Optional[Dict] = None) -> None:
    """Copy file from local or S3 path to local or S3 path.

    The parent directory of the output path is created if it doesn't exist.

    `boto3_kwargs` are forwarded to the respective call if boto3 is used.
    """
    boto3_kwargs = boto3_kwargs if (boto3_kwargs is not None) else {}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if (not isinstance(input_path, S3Path)) and (not isinstance(output_path, S3Path)):
        shutil.copy(input_path, output_path)
    elif isinstance(input_path, S3Path) and isinstance(output_path, S3Path):
        # Note: boto3.client('s3').copy_object works only for objects up to 5G in size.
        source = {"Bucket": input_path.bucket.name, "Key": str(input_path.key)}
        boto3.resource("s3").meta.client.copy(CopySource=source, Bucket=output_path.bucket.name, Key=str(output_path.key), **boto3_kwargs)
    elif (not isinstance(input_path, S3Path)) and isinstance(output_path, S3Path):
        boto3.resource("s3").meta.client.upload_file(Filename=str(input_path), Bucket=output_path.bucket.name, Key=str(output_path.key), **boto3_kwargs)
    elif isinstance(input_path, S3Path) and (not isinstance(output_path, S3Path)):
        boto3.resource("s3").meta.client.download_file(Bucket=input_path.bucket.name, Key=str(input_path.key), Filename=str(output_path), **boto3_kwargs)
    else:
        assert False


def cp_files(input_path: AnyPath, output_path: AnyPath, *, glob: str = "**/*", thread_pool_size: Optional[int] = os.cpu_count()) -> None:
    """Recursively copy files concurrently from glob pattern applied to the input local or S3 path to the output local or S3 path."""
    description = f"{glob} files from {path_to_uri(input_path)} to {path_to_uri(output_path)}"
    description += f" using a pool of {thread_pool_size} threads" if thread_pool_size else ""
    log.info(f"Copying {description}.")
    timer = Timer()
    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_pool_size) as pool:
        for input_file_path in input_path.glob(glob):
            if not input_file_path.is_file():
                continue
            output_file_path = output_path / input_file_path.relative_to(input_path)
            future = pool.submit(cp_file, input_file_path, output_file_path)
            futures.append(future)
        for future in concurrent.futures.as_completed(futures):
            future.result()
    log.info(f"Copied {len(futures):,} {description} in {timer}.")
