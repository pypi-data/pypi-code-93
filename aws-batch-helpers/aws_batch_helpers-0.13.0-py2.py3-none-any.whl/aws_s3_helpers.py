from botocore.exceptions import ClientError, EndpointConnectionError
from jinja2 import Environment, BaseLoader
import boto3
import botocore
import time
from pprint import pprint
from urllib.parse import urlparse
from typing import List, Set, Dict, Tuple, Optional
import os

import boto3

from mypy_boto3 import s3
import logging

s3_logger = logging.getLogger('s3_logger')


class S3Url(object):
    """
    Parse an S3 url into bucket, prefix and/or key
    https://stackoverflow.com/questions/42641315/s3-urls-get-bucket-name-and-path
    >>> s = S3Url("s3://bucket/hello/world")
    >>> s.bucket
    'bucket'
    >>> s.key
    'hello/world'
    >>> s.url
    's3://bucket/hello/world'

    >>> s = S3Url("s3://bucket/hello/world?qwe1=3#ddd")
    >>> s.bucket
    'bucket'
    >>> s.key
    'hello/world?qwe1=3#ddd'
    >>> s.url
    's3://bucket/hello/world?qwe1=3#ddd'

    >>> s = S3Url("s3://bucket/hello/world#foo?bar=2")
    >>> s.key
    'hello/world#foo?bar=2'
    >>> s.url
    's3://bucket/hello/world#foo?bar=2'
    """

    def __init__(self, url):
        self._parsed = urlparse(url, allow_fragments=False)

    @property
    def bucket(self):
        return self._parsed.netloc

    @property
    def key(self):
        if self._parsed.query:
            return self._parsed.path.lstrip('/') + '?' + self._parsed.query
        else:
            return self._parsed.path.lstrip('/')

    @property
    def url(self):
        return self._parsed.geturl()


def s3_key_exists(resource: s3.S3ServiceResource, bucket_name: str, key_path: str) -> bool:
    """Check if a given key exists in an s3 bucket

    Args:
        resource (s3.S3ServiceResource): resource: s3.S3ServiceResource = boto3.Session(region_name="us-west-1").resource("s3")
        key (str): key name to check for 
    Returns:
        [bool]: exists True/False 
    """
    if 's3://' in str(bucket_name):
        s3_bucket_url = S3Url(str(bucket_name))
        bucket_name = s3_bucket_url.bucket

    if 's3://' in str(key_path):
        s3_bucket_url = S3Url(str(key_path))
        key_path = s3_bucket_url.key

    try:
        resource.Object(bucket_name, key_path).load()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            s3_logger.info(f'Bucket: {bucket_name} Key: {key_path} not found')
            return False
        else:
            # Something else has gone wrong.
            s3_logger.exception("Exception occurred")
            return False
    s3_logger.info(f'Bucket: {bucket_name} Key: {key_path} found')
    return True


def s3_bucket_exists(resource: s3.S3ServiceResource, bucket_name: str) -> bool:
    """Check if a bucket exists

    Args:
        resource (s3.S3ServiceResource): resource: s3.S3ServiceResource = boto3.Session(region_name="us-west-1").resource("s3")
        bucket_name (str): s3 bucket name to check for 

    Returns:
        [bool]: exists True/False 
    """
    if 's3://' in str(bucket_name):
        s3_bucket_url = S3Url(str(bucket_name))
        bucket_name = s3_bucket_url.bucket

    bucket = resource.Bucket(bucket_name)

    if bucket.creation_date:
        return True
    else:
        return False


def prefix_exists(client: s3.S3Client, bucket_name: str, prefix: str) -> bool:
    """Check if S3 prefix exists - Prefix is like a file path

    Args:
        client (s3.S3Client): client = boto3.client('s3')
        bucket_name (str): [description]
        prefix (str): [description]

    Returns:
        [bool]: exists True/False 
    """
    try:
        res = client.list_objects_v2(
            Bucket=bucket_name, Prefix=prefix, MaxKeys=1)
    except Exception as e:
        return False

    if len(res['Contents']):
        return True
    else:
        return False
