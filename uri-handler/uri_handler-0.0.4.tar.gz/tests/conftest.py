import os

import marshmallow
import pytest


from file_testing import temp_file_base_uri

# test s3 if boto3 configured
try:
    from s3_testing import mock_s3_base_uri
    can_s3 = True
except ImportError as e:
    if e == "boto3":
        can_s3 = False
    else:
        raise


# determine which components to test_test based on environment
b = marshmallow.fields.Boolean()
test_s3 = b.deserialize(os.environ.get("UH_TEST_S3", True))
test_file = b.deserialize(os.environ.get("UH_TEST_FILE", True))


@pytest.fixture(scope="module")
def s3_uri_fixture():
    with mock_s3_base_uri(include_query=False) as uri:
        yield uri


@pytest.fixture(scope="module")
def file_uri_fixture():
    with temp_file_base_uri() as uri:
        yield uri


# this is a workaround for parametrizing fixtures
uribase_fixtures_to_test = (
    ["file_uri_fixture" if test_file else []] +
    ["s3_uri_fixture"] if (can_s3 or test_s3) else [])
