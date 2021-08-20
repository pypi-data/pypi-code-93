from datetime import timedelta

import pytest

from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN

from django.contrib.auth.models import Permission


ONE_HOUR = timedelta(hours=1)
TWO_HOURS = timedelta(hours=2)


def test_admin_user_can_update_sessions(admin_client, session):
    response = update_session(admin_client, session)

    assert_success(response)
    assert_session_is_updated(session)


def test_admin_user_can_partial_update_sessions(admin_client, session):
    response = partial_update_session(admin_client, session)

    assert_success(response)
    assert_session_is_updated(session)


def test_user_with_permission_can_update_sessions(client, user, session):
    update_permission = Permission.objects.get(codename='change_session',
                                               content_type__app_label='projects')
    user.user_permissions.add(update_permission)

    response = update_session(client, session)

    assert_success(response)
    assert_session_is_updated(session)


def test_user_with_permission_can_partial_update_sessions(client, user, session):
    update_permission = Permission.objects.get(codename='change_session',
                                               content_type__app_label='projects')
    user.user_permissions.add(update_permission)

    response = partial_update_session(client, session)

    assert_success(response)
    assert_session_is_updated(session)


def test_user_without_permission_can_update_sessions(client, session):
    response = update_session(client, session)

    assert_success(response)
    assert_session_is_updated(session)


def test_user_without_permission_can_partial_update_sessions(client, session):
    response = partial_update_session(client, session)

    assert_success(response)
    assert_session_is_updated(session)


@pytest.mark.django_db
def test_anonymous_user_cannot_update_sessions(anonymous_client, session):
    response = update_session(anonymous_client, session)

    assert_permission_denied(response)
    assert_session_did_not_change(session)


@pytest.mark.django_db
def test_anonymous_user_cannot_partial_update_sessions(anonymous_client, session):
    response = partial_update_session(anonymous_client, session)

    assert_permission_denied(response)
    assert_session_did_not_change(session)


def update_session(client, session):
    return client.put(
        reverse('session-detail', kwargs=dict(pk=session.id)),
        data=dict(
            experiment=session.experiment.pk,
            order=session.order,
            title='new title',
            setup_time=session.setup_time,
            duration=TWO_HOURS,
            teardown_time=session.teardown_time,
            operator=session.operator.pk,
            max_number_of_participants=session.max_number_of_participants,
        )
    )


def partial_update_session(client, session):
    return client.patch(
        reverse('session-detail', kwargs=dict(pk=session.id)),
        data=dict(duration=TWO_HOURS, title='new title')
    )


def assert_success(response):
    assert response.status_code == HTTP_200_OK


def assert_session_is_updated(session):
    session.refresh_from_db()
    assert TWO_HOURS == session.duration
    assert 'new title' == session.title


def assert_permission_denied(response):
    assert response.status_code == HTTP_403_FORBIDDEN


def assert_session_did_not_change(session):
    session.refresh_from_db()
    assert ONE_HOUR == session.duration
