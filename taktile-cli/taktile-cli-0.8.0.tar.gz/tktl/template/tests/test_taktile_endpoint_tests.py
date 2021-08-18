import pytest
from src.endpoints import tktl


@pytest.mark.parametrize(
    "endpoint",
    [
        endpoint
        for endpoint in tktl.endpoints
        if endpoint.input_schema.value is not None
        and not endpoint.disable_rest_validation
    ],
)
def test_endpoints(json_metadata, endpoint):
    """test_endpoints.
    This test ensures the provided sample data on endpoints can be correctly
    processed by the endpoints.

    It is recommended to keep these tests around.
    """

    function = endpoint._func
    function_name = function.__name__

    json_metadata["section"] = "Taktile Automatic Endpoint Tests"
    json_metadata["pass_message"] = f"Sample data for {function_name} is valid"
    json_metadata["fail_message"] = f"Sample data for {function_name} is invalid"

    function(endpoint.input_schema.value)
