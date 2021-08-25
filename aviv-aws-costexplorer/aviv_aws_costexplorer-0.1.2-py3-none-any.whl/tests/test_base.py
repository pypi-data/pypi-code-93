import pytest
import boto3.session
import botocore.client
from aviv_aws_costexplorer import base


@pytest.fixture
def aacli():
    return base.AWSClient()


def test_awsclient(aacli):
    assert isinstance(aacli, base.AWSClient)

    assert isinstance(aacli.sts, botocore.client.BaseClient)
    assert isinstance(aacli.account_id, str)

    assert isinstance(aacli.client('ce'), botocore.client.BaseClient)
    assert isinstance(aacli.session(), boto3.session.Session)


def test_sts_credentials(aacli):
    creds = base.AWSClient.sts_credentials(dict(
        Credentials={
            'AccessKeyId': 'abc',
            'SecretAccessKey': 'def',
            'SessionToken': 'ghi'
        }
    ))
    assert 'aws_access_key_id' in creds
    assert 'aws_secret_access_key' in creds
    assert 'aws_session_token' in creds
    with pytest.raises(KeyError):
        base.AWSClient.sts_credentials({})
