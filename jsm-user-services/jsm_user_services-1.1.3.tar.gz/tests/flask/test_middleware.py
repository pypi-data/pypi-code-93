import pytest
from flask.testing import FlaskClient

from jsm_user_services.services.user import get_session_id_from_bearer_token


def test_should_retrieve_authorization_token_that_is_set_on_local_threading(flask_test_client: FlaskClient):
    response = flask_test_client.get("/authorization-token", headers={"Authorization": "Bearer abc"})

    assert response.status_code == 200
    assert response.json == {"auth_token": "abc"}


@pytest.mark.parametrize("ips_string,expected_ip", [("8.8.8.8", "8.8.8.8"), ("7.7.7.7, 8.8.8.8, 9.9.9.9", "7.7.7.7")])
def test_should_retrieve_user_ip_that_is_set_on_local_threading(
    flask_test_client: FlaskClient, ips_string: str, expected_ip: str
):
    response = flask_test_client.get("/my-ip", headers={"x-original-forwarded-for": ips_string})

    assert response.status_code == 200
    assert response.json == {"ip": expected_ip}


def test_should_retrieve_user_session_id_that_is_set_on_local_threading(flask_test_client: FlaskClient):
    response = flask_test_client.get("/session-id", headers={"Authorization": "Bearer abc"})

    assert response.status_code == 200
    assert response.json == {"session_id": get_session_id_from_bearer_token("abc")}
