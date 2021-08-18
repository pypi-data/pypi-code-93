import os

import pytest

from tktl.core.clients.rest import RestClient
from tktl.core.exceptions import TaktileSdkError
from tktl.core.managers.auth import AuthConfigManager


def test_instantiate_client():

    key = os.environ["TEST_USER_API_KEY"]
    AuthConfigManager.set_api_key(key)

    with pytest.raises(TaktileSdkError):
        RestClient(
            api_key=key,
            repository_name=f"{os.environ['TEST_USER']}/test-new",
            branch_name="master",
            endpoint_name="repayment",
        )

    client = RestClient(
        api_key=key,
        repository_name=f"{os.environ['TEST_USER']}/integ-testing",
        branch_name="master",
        endpoint_name="repayment",
    )
    assert client.location is not None


def test_instantiate_by_url(sample_deployed_url):
    key = os.environ["TEST_USER_API_KEY"]
    AuthConfigManager.set_api_key(key)
    client = RestClient.for_url(
        api_key=key, url=sample_deployed_url, endpoint_name="repayment"
    )
    assert client.location == f"https://{sample_deployed_url}/"
