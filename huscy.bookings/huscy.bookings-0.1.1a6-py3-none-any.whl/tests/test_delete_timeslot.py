import pytest

from django.contrib.auth.models import Permission
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from huscy.bookings.models import Timeslot


@pytest.mark.django_db
def test_admin_user_can_delete_timeslots(admin_client, timeslot):
    response = delete_timeslot(admin_client, timeslot)

    assert_success(response)
    assert_timeslot_deleted(timeslot)


@pytest.mark.django_db
def test_user_with_permission_can_delete_timeslots(client, user, timeslot):
    delete_permission = Permission.objects.get(codename='delete_timeslot')
    user.user_permissions.add(delete_permission)

    response = delete_timeslot(client, timeslot)

    assert_success(response)
    assert_timeslot_deleted(timeslot)


@pytest.mark.django_db
def test_user_without_permission_cannot_delete_timeslots(client, timeslot):
    response = delete_timeslot(client, timeslot)

    assert_permission_denied(response)
    assert_timeslot_still_exists(timeslot)


@pytest.mark.django_db
def test_anonymous_user_cannot_delete_timeslots(client, timeslot):
    client.logout()

    response = delete_timeslot(client, timeslot)

    assert_permission_denied(response)
    assert_timeslot_still_exists(timeslot)


@pytest.mark.django_db
def test_delete_booked_timeslot(client, user, booked_timeslot):
    delete_permission = Permission.objects.get(codename='delete_timeslot')
    user.user_permissions.add(delete_permission)

    response = delete_timeslot(client, booked_timeslot)

    assert_bad_request(response)
    assert_timeslot_still_exists(booked_timeslot)


def delete_timeslot(client, timeslot):
    return client.delete(reverse('timeslot-detail', kwargs=dict(pk=timeslot.pk)))


def assert_success(response):
    assert response.status_code == HTTP_204_NO_CONTENT


def assert_bad_request(response):
    assert response.status_code == HTTP_400_BAD_REQUEST


def assert_permission_denied(response):
    assert response.status_code == HTTP_403_FORBIDDEN


def assert_timeslot_deleted(timeslot):
    assert not Timeslot.objects.filter(pk=timeslot.pk).exists()


def assert_timeslot_still_exists(timeslot):
    assert Timeslot.objects.filter(pk=timeslot.pk).exists()
