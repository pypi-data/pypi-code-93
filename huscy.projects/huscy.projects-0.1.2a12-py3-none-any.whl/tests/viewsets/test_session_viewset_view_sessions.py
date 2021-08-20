import pytest

from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN


def test_admin_user_can_list_sessions(admin_client):
    response = list_sessions(admin_client)

    assert_success(response)


def test_user_without_permission_can_list_sessions(client):
    response = list_sessions(client)

    assert_success(response)


@pytest.mark.django_db
def test_anonymous_user_cannot_list_sessions(anonymous_client):
    response = list_sessions(anonymous_client)

    assert_permission_denied(response)


def retrieve_session(client, session):
    return client.get(reverse('session-detail', kwargs=dict(pk=session.id)))


def list_sessions(client):
    return client.get(reverse('session-list'))


def assert_success(response):
    assert response.status_code == HTTP_200_OK


def assert_permission_denied(response):
    assert response.status_code == HTTP_403_FORBIDDEN
