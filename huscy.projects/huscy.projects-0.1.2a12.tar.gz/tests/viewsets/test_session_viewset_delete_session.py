import pytest

from rest_framework.reverse import reverse
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_403_FORBIDDEN

from django.contrib.auth.models import Permission

pytestmark = pytest.mark.django_db


def test_admin_user_can_delete_projects(admin_client, session):
    response = delete_session(admin_client, session)

    assert response.status_code == HTTP_204_NO_CONTENT


def test_user_with_permission_can_delete_projects(client, user, session):
    delete_permission = Permission.objects.get(codename='delete_session',
                                               content_type__app_label='projects')
    user.user_permissions.add(delete_permission)

    response = delete_session(client, session)

    assert response.status_code == HTTP_204_NO_CONTENT


def test_user_without_permission_can_delete_projects(client, session):
    response = delete_session(client, session)

    assert response.status_code == HTTP_204_NO_CONTENT


def test_anonymous_user_cannot_delete_projects(anonymous_client, session):
    response = delete_session(anonymous_client, session)

    assert response.status_code == HTTP_403_FORBIDDEN


def delete_session(client, session):
    return client.delete(reverse('session-detail', kwargs=dict(pk=session.pk)))
