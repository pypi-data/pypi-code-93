import pytest

from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN

pytestmark = pytest.mark.django_db


def test_admin_user_can_view_projects(admin_client):
    response = list_projects(admin_client)

    assert response.status_code == HTTP_200_OK


def test_user_without_permission_can_view_projects(client):
    response = list_projects(client)

    assert response.status_code == HTTP_200_OK


def test_anonymous_user_cannot_view_projects(anonymous_client):
    response = list_projects(anonymous_client)

    assert response.status_code == HTTP_403_FORBIDDEN


def list_projects(client):
    return client.get(reverse('project-list'))


def retrieve_project(client, project):
    return client.get(reverse('project-detail', kwargs=dict(pk=project.pk)))
