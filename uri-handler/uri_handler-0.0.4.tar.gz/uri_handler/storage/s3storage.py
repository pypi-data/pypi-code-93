"""
boto3-based s3 uri utilities
"""
import boto3
import botocore.config
from botocore.utils import fix_s3_host

from uri_handler.storage.marsh import (
    load_s3session_dict, load_s3resource_dict
)
from uri_handler.utils._compat import (
    urllib,
    pathlib)

default_config = botocore.config.Config()


def parse_s3_uri(uri):
    parsed_uri = urllib.parse.urlparse(uri)

    bucket = parsed_uri.netloc
    path = parsed_uri.path.lstrip('/')  # TODO is stripping necessary?
    return bucket, path


def s3resource_writebytes(b, bucket, fn, resource=None):
    resource.Object(bucket, fn).put(Body=b)


def s3resource_writebytes_uri(b, uri, resource=None):
    bucket, path = parse_s3_uri(uri)
    return s3resource_writebytes(b, bucket, path, resource)


def s3resource_readbytes(bucket, fn, resource=None):
    return resource.Object(bucket, fn).get()["Body"].read()


def s3_readbytes_uri(uri, resource=None):
    bucket, path = parse_s3_uri(uri)
    return s3resource_readbytes(bucket, path, resource)


def get_s3_session_resource_from_uri(uri, config=default_config):
    """generate s3 resource from custom uri string"""
    p = urllib.parse.urlparse(uri)
    queryparams = urllib.parse.parse_qs(p.query)
    sessionparams = load_s3session_dict(queryparams)
    resourceparams = load_s3resource_dict(queryparams)

    session = boto3.session.Session(**sessionparams)
    resource = session.resource('s3', config=config, **resourceparams)

    resource.meta.client.meta.events.unregister(
        "before-sign.s3", fix_s3_host)
    return session, resource


def s3_listuris_from_prefix(uri, resource=None):
    # bucket, path = parse_s3_uri(uri)
    parsed_uri = urllib.parse.urlparse(uri)
    for obj in resource.Bucket(parsed_uri.netloc).objects.filter(
            Prefix=parsed_uri.path.lstrip('/')):
        yield urllib.parse.urlunparse(urllib.parse.ParseResult(
            parsed_uri.scheme,
            obj.bucket_name,
            obj.key,
            parsed_uri.params,
            parsed_uri.query,
            parsed_uri.fragment))


def s3_uri_exists(uri, resource=None):
    bucket, path = parse_s3_uri(uri)
    for obj in resource.Bucket(bucket).objects.filter(Prefix=path):
        return True
    return False


def s3_validate_prefix(uri, resource=None, **kwargs):
    # TODO this should include a check_writable like the file version
    bucket, path = parse_s3_uri(uri)
    try:
        resource.meta.client.head_bucket(Bucket=bucket)
        return True
    except botocore.client.ClientError:
        return False


class S3UriHandler:
    def save_bytes(self, b, uri):
        session, resource = get_s3_session_resource_from_uri(uri)
        s3resource_writebytes_uri(b, uri, resource=resource)

    def write_bytes(self, uri, b):
        return self.save_bytes(b, uri)

    def read_bytes(self, uri):
        session, resource = get_s3_session_resource_from_uri(uri)
        return s3_readbytes_uri(uri, resource=resource)

    def list_uris_prefix(self, uri_prefix):
        session, resource = get_s3_session_resource_from_uri(uri_prefix)
        return s3_listuris_from_prefix(uri_prefix, resource=resource)

    def validate_prefix(self, uri_prefix, **kwargs):
        session, resource = get_s3_session_resource_from_uri(uri_prefix)
        return s3_validate_prefix(uri_prefix, resource=None)
