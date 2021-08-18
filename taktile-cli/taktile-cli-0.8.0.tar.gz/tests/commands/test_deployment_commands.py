import pytest
from pydantic import UUID4

from tktl.commands.deployments import GetDeployments, GetEndpoints
from tktl.core.exceptions.exceptions import APIClientException
from tktl.login import logout


def test_get_deployment_commands(logged_in_context):
    cmd = GetDeployments()
    result = cmd.execute(
        UUID4("33fb5b8f-e6a2-4dd2-86ef-d257d2c59b85"),
        None,
        None,
        None,
        None,
        None,
        return_all=False,
    )
    assert len(result) == 1

    result = cmd.execute(None, None, None, None, None, None, return_all=True)
    assert len(result) >= 5

    cmd = GetEndpoints()
    result = cmd.execute(
        UUID4("395391a4-a4c8-4671-8dc4-9423fecb5e4a"),
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )
    assert len(result) == 4

    cmd = GetDeployments()
    with pytest.raises(APIClientException):
        logout()
        cmd.execute(
            UUID4("7c0f6f48-0220-450a-b4d2-bfc731f94cc3"),
            None,
            None,
            None,
            None,
            None,
            return_all=True,
        )
