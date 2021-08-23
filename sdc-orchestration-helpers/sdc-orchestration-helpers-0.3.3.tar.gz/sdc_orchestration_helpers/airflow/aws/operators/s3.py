# pylint: disable=super-with-arguments
# pylint: disable=redefined-builtin
# pylint: disable=invalid-name

"""SDC Custom S3 Operators"""
"""SDC Custom S3 Operators"""
import os
import logging
from urllib.parse import urlparse
import boto3
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

logger = logging.getLogger(None)

def parse_s3_url(url):
    """Returns an (s3 bucket, key name/prefix) tuple from a url with an s3 scheme.
    Args:
        url (str):
    Returns:
        tuple: A tuple containing:
            - str: S3 bucket name
            - str: S3 key
    """
    parsed_url = urlparse(url)
    if parsed_url.scheme != "s3":
        raise ValueError("Expecting 's3' scheme, got: {} in {}.".format(parsed_url.scheme, url))
    return parsed_url.netloc, parsed_url.path.lstrip("/")

class CopyBetweenS3Locations(BaseOperator):
    template_fields = ('dst_path', 'src_path', 'keep_filename', 'xcom_tasks' )

    @apply_defaults
    def __init__(self, dst_path, src_path=None, keep_filename=False, xcom_tasks=None, *args, **kwargs):
        super(CopyBetweenS3Locations, self).__init__(*args, **kwargs)
        self.dst_path = dst_path
        self.src_path = src_path
        self.xcom_tasks = xcom_tasks
        self.keep_filename = keep_filename

    def execute(self, context):
        """ Copy s3 object between two buckets
        """
        # init boto session and sagemaker
        BOTO_SESSION = boto3.Session()
        SM_RESOURCE = BOTO_SESSION.resource('s3')

        try:
            if self.src_path is None:
                self.src_path = context['task_instance'].xcom_pull(
                    task_ids=self.xcom_tasks['src_path']['task_id'],
                    key=self.xcom_tasks['src_path']['key']
                )
                assert self.src_path is not None, "No source path found. Either hardcode in config or pass from previous job"

            src_bucket, src_filepath = parse_s3_url(self.src_path)
            dst_bucket, dst_filepath = parse_s3_url(self.dst_path)

            if self.keep_filename:
                # assumes destination path is a folder path
                # keeps src filename
                src_filename = src_filepath.split('/')[-1]
                logger.info("Keep source filename = {}".format(src_filename))
                # assumes dst_path given without filename
                dst_filepath = os.path.join(dst_filepath, src_filename)
                # assumes dst_path is given without filename
                self.dst_path = os.path.join(self.dst_path, src_filename)

            copy_source = {
                'Bucket': src_bucket,
                'Key': src_filepath
            }
            bucket = SM_RESOURCE.Bucket(dst_bucket)
            bucket.copy(copy_source, dst_filepath)

            # push response up
            context['task_instance'].xcom_push(
                key='destination_location',
                value=self.dst_path
            )

        except Exception as exception:
            raise exception
