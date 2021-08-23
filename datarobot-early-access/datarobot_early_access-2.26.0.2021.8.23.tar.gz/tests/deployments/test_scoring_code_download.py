from tempfile import NamedTemporaryFile

import pytest
import responses

from datarobot import Deployment


@pytest.fixture
def scoring_code_data(deployment_data):
    return b"scoring_code_jar_file_data"


@pytest.fixture
def scoring_code_retrieve_response(unittest_endpoint, deployment_data, scoring_code_data):
    url = "{}/deployments/{}/scoringCode/".format(unittest_endpoint, deployment_data["id"])
    responses.add(
        responses.GET,
        url,
        status=200,
        content_type="application/java-archive",
        body=scoring_code_data,
    )


@pytest.fixture
def scoring_code_build_response(unittest_endpoint, deployment_data):
    status_url = "{}/status_url".format(unittest_endpoint)
    scoring_code_build_url = "{}/deployments/{}/scoringCodeBuilds/".format(
        unittest_endpoint, deployment_data["id"]
    )
    scoring_code_retrieve_url = "{}/deployments/{}/scoringCode/".format(
        unittest_endpoint, deployment_data["id"]
    )

    responses.add(
        responses.GET, status_url, headers={"Location": scoring_code_retrieve_url}, status=303
    )
    responses.add(
        responses.POST, scoring_code_build_url, headers={"Location": status_url}, status=202
    )


@responses.activate
@pytest.mark.usefixtures("deployment_get_response", "scoring_code_retrieve_response")
def test_download_scoring_code_without_build(deployment_data, scoring_code_data):
    """Test download_scoring_code that does not require building."""

    with NamedTemporaryFile() as file:
        deployment = Deployment.get(deployment_data["id"])
        deployment.download_scoring_code(file.name, include_agent=False)
        assert file.read() == scoring_code_data


@responses.activate
@pytest.mark.usefixtures(
    "deployment_get_response", "scoring_code_build_response", "scoring_code_retrieve_response"
)
def test_download_scoring_code_with_build(deployment_data, scoring_code_data):
    """Test download_scoring_code that requires building first."""

    with NamedTemporaryFile() as file:
        deployment = Deployment.get(deployment_data["id"])
        deployment.download_scoring_code(file.name, include_agent=True)
        assert file.read() == scoring_code_data
