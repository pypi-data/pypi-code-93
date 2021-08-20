from datetime import timedelta

import pytest

from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_403_FORBIDDEN

from django.contrib.auth.models import Permission

pytestmark = pytest.mark.django_db


def test_admin_user_can_create_sessions(admin_client, user, experiment):
    response = create_session(admin_client, experiment, user)

    assert response.status_code == HTTP_201_CREATED


def test_user_with_permission_can_create_sessions(client, user, experiment):
    create_permission = Permission.objects.get(codename='add_session',
                                               content_type__app_label='projects')
    user.user_permissions.add(create_permission)

    response = create_session(client, experiment, user)

    assert response.status_code == HTTP_201_CREATED


def test_user_without_permission_can_create_sessions(client, user, experiment):
    response = create_session(client, experiment, user)

    assert response.status_code == HTTP_201_CREATED


def test_anonymous_user_cannot_create_sessions(anonymous_client, user, experiment):
    response = create_session(anonymous_client, experiment, user)

    assert response.status_code == HTTP_403_FORBIDDEN


def create_session(client, experiment, operator):
    return client.post(
        reverse('session-list'),
        data=dict(
            experiment=experiment.pk,
            operator=operator.pk,
            duration=timedelta(hours=1),
        )
    )
