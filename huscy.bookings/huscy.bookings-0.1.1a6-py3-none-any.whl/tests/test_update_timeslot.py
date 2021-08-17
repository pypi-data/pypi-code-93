from datetime import datetime

import pytest

from django.contrib.auth.models import Permission
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from huscy.bookings.models import Timeslot


@pytest.mark.django_db
def test_admin_user_can_update_timeslots(admin_client, timeslot):
    response = update_timeslot(admin_client, timeslot)

    assert_success(response)
    assert_timeslot_updated(response, timeslot)


@pytest.mark.django_db
def test_user_with_permission_can_update_timeslots(client, user, timeslot):
    change_permission = Permission.objects.get(codename='change_timeslot')
    user.user_permissions.add(change_permission)

    response = update_timeslot(client, timeslot)

    assert_success(response)
    assert_timeslot_updated(response, timeslot)


@pytest.mark.django_db
def test_user_without_permission_cannot_update_timeslots(client, timeslot):
    response = update_timeslot(client, timeslot)

    assert_permission_denied(response)
    assert_timeslot_not_updated(timeslot)


@pytest.mark.django_db
def test_anonymous_user_cannot_update_timeslots(client, timeslot):
    client.logout()

    response = update_timeslot(client, timeslot)

    assert_permission_denied(response)
    assert_timeslot_not_updated(timeslot)


@pytest.mark.django_db
def test_move_booked_timeslot(client, user, booked_timeslot):
    change_permission = Permission.objects.get(codename='change_timeslot')
    user.user_permissions.add(change_permission)

    response = update_timeslot(client, booked_timeslot)

    assert_bad_request(response)
    assert_timeslot_not_updated(booked_timeslot)


@pytest.mark.django_db
def test_active_flag_when_moved_timeslot_overlaps_with_booked(client, user, booked_timeslot,
                                                              timeslot):
    change_permission = Permission.objects.get(codename='change_timeslot')
    user.user_permissions.add(change_permission)

    response = update_timeslot(client, timeslot)

    assert_active_flag(response, False)


@pytest.mark.django_db
def test_active_flag_when_moved_timeslot_does_not_overlap_with_booked(client, user, booked_timeslot,
                                                                      timeslot):
    change_permission = Permission.objects.get(codename='change_timeslot')
    user.user_permissions.add(change_permission)

    response = update_timeslot(client, timeslot, datetime(2000, 1, 1, 8))

    assert_active_flag(response, True)


def update_timeslot(client, timeslot, start=datetime(2000, 1, 1, 10)):
    return client.put(
        reverse('timeslot-detail', kwargs=dict(pk=timeslot.pk)),
        data=dict(
            session=timeslot.session.pk,
            start=start,
        )
    )


def assert_success(response):
    assert response.status_code == HTTP_200_OK


def assert_bad_request(response):
    assert response.status_code == HTTP_400_BAD_REQUEST


def assert_permission_denied(response):
    assert response.status_code == HTTP_403_FORBIDDEN


def assert_timeslot_updated(response, timeslot):
    timeslot.refresh_from_db()
    assert timeslot.start.hour == 10


def assert_timeslot_not_updated(timeslot):
    timeslot.refresh_from_db()
    assert timeslot.start.hour == 12


def assert_active_flag(response, expected_active_value):
    assert response.json()['active'] is expected_active_value
    assert Timeslot.objects.filter(active=expected_active_value).exists()
