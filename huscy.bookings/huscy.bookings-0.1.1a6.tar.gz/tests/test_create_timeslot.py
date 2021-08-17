from datetime import datetime

import pytest

from django.contrib.auth.models import Permission
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_403_FORBIDDEN

from huscy.bookings.models import Timeslot


@pytest.mark.django_db
def test_admin_user_can_create_timeslots(admin_client, session):
    response = create_timeslot(admin_client, session)

    assert_success(response)
    assert_new_timeslot_exists()


@pytest.mark.django_db
def test_user_with_permission_can_create_timeslots(client, user, session):
    create_permission = Permission.objects.get(codename='add_timeslot')
    user.user_permissions.add(create_permission)

    response = create_timeslot(client, session)

    assert_success(response)
    assert_new_timeslot_exists()


@pytest.mark.django_db
def test_user_without_permission_cannot_create_timeslots(client, session):
    response = create_timeslot(client, session)

    assert_permission_denied(response)
    assert_timeslot_does_not_exist()


@pytest.mark.django_db
def test_anonymous_user_cannot_create_timeslots(client, session):
    client.logout()

    response = create_timeslot(client, session)

    assert_permission_denied(response)
    assert_timeslot_does_not_exist()


@pytest.mark.django_db
def test_active_flag_when_new_timeslot_overlaps_with_booked(client, user, booked_timeslot,
                                                            data_acquisition_method):
    create_permission = Permission.objects.get(codename='add_timeslot')
    user.user_permissions.add(create_permission)

    response = create_timeslot(client, data_acquisition_method.session)

    assert_active_flag(response, False)


@pytest.mark.django_db
def test_active_flag_when_new_timeslot_does_not_overlap_with_booked(client, user, booked_timeslot,
                                                                    data_acquisition_method):
    create_permission = Permission.objects.get(codename='add_timeslot')
    user.user_permissions.add(create_permission)

    response = create_timeslot(client, data_acquisition_method.session, datetime(2000, 1, 1, 8))

    assert_active_flag(response, True)


def create_timeslot(client, session, start=datetime(2000, 1, 1, 12)):
    return client.post(
        reverse('timeslot-list'),
        data=dict(
            session=session.pk,
            start=start,
        )
    )


def assert_success(response):
    assert response.status_code == HTTP_201_CREATED


def assert_permission_denied(response):
    assert response.status_code == HTTP_403_FORBIDDEN


def assert_new_timeslot_exists():
    assert Timeslot.objects.exists()


def assert_timeslot_does_not_exist():
    assert not Timeslot.objects.exists()


def assert_active_flag(response, expected_active_value):
    assert response.json()['active'] is expected_active_value
    assert Timeslot.objects.filter(active=expected_active_value).exists()
