import os

import pytest

from tktl.core.clients import DeploymentApiClient
from tktl.core.config import settings
from tktl.core.exceptions import TaktileSdkError
from tktl.core.managers.auth import AuthConfigManager


def test_instantiate_taktile_client():
    key = os.environ["TEST_USER_API_KEY"]
    AuthConfigManager.set_api_key(key)
    client = DeploymentApiClient()
    with pytest.raises(TaktileSdkError):
        client.get_endpoint_by_name("admin/df.asfm", "", "")
    assert "X-Api-Key" in client.default_headers
    assert client.default_headers["X-Api-Key"] == key
    assert (
        client.get_path(f"{settings.API_V1_STR}/deployments")
        == f"{settings.DEPLOYMENT_API_URL}{settings.API_V1_STR}/deployments"
    )
