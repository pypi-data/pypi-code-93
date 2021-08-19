import boto3
import botocore
import time
from datetime import datetime
import pyarrow as pa
import pyarrow.parquet as pq
from s3transfer import S3UploadFailedError
from s3fs import S3FileSystem
from airflow_commons.logger import LOGGER

DEFAULT_RETRY_COUNT = 3


def get_param(key, region_name: str = "eu-west-1"):
    ssm = boto3.client("ssm", region_name=region_name)
    parameter = ssm.get_parameter(Name=key, WithDecryption=True)
    return parameter["Parameter"]["Value"]


def upload_file_to_s3_bucket(path_to_file: str, bucket_name: str, file_name: str):
    """
    Uploads the given file to the given s3 bucket.

    :param path_to_file: Path to file that will be uploaded to s3 bucket.
    :param bucket_name: Name of the bucket that file will be uploaded to.
    :param file_name: Name of the file (key of the file in s3).
    """
    LOGGER("Upload to " + bucket_name + " started")
    upload_start = datetime.now()
    s3_client = boto3.client("s3")
    try:
        s3_client.upload_file(path_to_file, bucket_name, file_name)
    except S3UploadFailedError as e:
        LOGGER("Upload to " + bucket_name + " failed")
        raise e
    upload_end = datetime.now()
    LOGGER(
        "Upload finished in {duration} seconds".format(
            duration=round((upload_end - upload_start).total_seconds())
        )
    )


def write_into_s3_file(
    bucket_name: str,
    file_name: str,
    data: str,
    key: str = None,
    secret: str = None,
    retry_count: int = DEFAULT_RETRY_COUNT,
):
    """
    Writes the given string data into the specified file in the specified bucket. If file does not exists create one, if
    exists overrides it. If the aws key and secret is not given, method uses the environmental variables as credentials.

    :param bucket_name: Name of the bucket that the target file is stored
    :param file_name: Name of the file that will be overridden
    :param data: A string contains the content of the file
    :param key: AWS access key id, default is None
    :param secret: AWS secret access key, default is None
    :param retry_count: retry count for S3 upload equals to three on default
    """

    LOGGER("Writing to " + bucket_name + "/" + file_name + " started")
    writing_start = datetime.now()
    total_upload_tries = 0
    while total_upload_tries <= retry_count:
        if key is not None and secret is not None:
            s3 = S3FileSystem(key=key, secret=secret)
        else:
            s3 = S3FileSystem()
        with s3.open(bucket_name + "/" + file_name, "w") as f:
            try:
                f.write(data)
                break
            except botocore.exceptions.NoCredentialsError as e:
                total_upload_tries = total_upload_tries + 1
                if total_upload_tries == retry_count:
                    raise e
                time.sleep(1)
    writing_end = datetime.now()
    LOGGER(
        (
            "Writing finished in ",
            round((writing_end - writing_start).total_seconds()),
            " seconds",
        )
    )


def write_to_s3_with_parquet(bucket_name: str, container_name: str, table: pa.Table):
    """
    Writes the given string data into the specified file in the specified bucket.
    :param bucket_name: Name of the bucket that the target file is stored
    :param container_name: Name of the container that will be overridden
    :param table: Table that will be written to the dataset whose filepath created by bucket_name and container_name
    """
    output_file = f"s3://{bucket_name}/{container_name}"
    s3 = S3FileSystem()
    pq.write_to_dataset(table=table, root_path=output_file, filesystem=s3)
