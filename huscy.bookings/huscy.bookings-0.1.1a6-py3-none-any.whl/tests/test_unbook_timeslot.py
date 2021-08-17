import pytest
from model_bakery import baker

from django.contrib.auth.models import Permission

from rest_framework.reverse import reverse
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_403_FORBIDDEN

from huscy.appointments.models import Appointment


@pytest.mark.django_db
def test_admin_user_can_unbook_timeslots(admin_client, booked_timeslot):
    response = unbook_timeslot(admin_client, booked_timeslot)

    assert_success(response)
    assert_timeslot_unbooked(booked_timeslot)


@pytest.mark.django_db
def test_user_with_permission_can_unbook_timeslots(client, user, booked_timeslot):
    unbook_permission = Permission.objects.get(codename='delete_booking')
    user.user_permissions.add(unbook_permission)

    response = unbook_timeslot(client, booked_timeslot)

    assert_success(response)
    assert_timeslot_unbooked(booked_timeslot)


@pytest.mark.django_db
def test_user_without_permission_cannot_unbook_timeslots(client, booked_timeslot):
    response = unbook_timeslot(client, booked_timeslot)

    assert_permission_denied(response)
    assert_timeslot_still_booked(booked_timeslot)


@pytest.mark.django_db
def test_anonymous_user_cannot_unbook_timeslots(client, booked_timeslot):
    client.logout()

    response = unbook_timeslot(client, booked_timeslot)

    assert_permission_denied(response)
    assert_timeslot_still_booked(booked_timeslot)


@pytest.mark.django_db
def test_unbook_timeslot_with_unbooked_timeslot(client, user, timeslot):
    unbook_permission = Permission.objects.get(codename='delete_booking')
    user.user_permissions.add(unbook_permission)

    response = unbook_timeslot(client, timeslot)

    assert_success(response)
    assert_timeslot_unbooked(timeslot)


@pytest.mark.django_db
def test_unbook_timeslot_with_multiple_bookings_for_timeslot(client, user, booked_timeslot):
    unbook_permission = Permission.objects.get(codename='delete_booking')
    user.user_permissions.add(unbook_permission)

    appointment = baker.make('appointments.Appointment')
    baker.make('bookings.Booking', appointment=appointment, timeslot=booked_timeslot)

    response = unbook_timeslot(client, booked_timeslot)

    assert_success(response)
    assert_timeslot_unbooked(booked_timeslot)


@pytest.mark.django_db
def test_unbooked_timeslot_is_set_to_active(client, user, booked_timeslot):
    unbook_permission = Permission.objects.get(codename='delete_booking')
    user.user_permissions.add(unbook_permission)

    response = unbook_timeslot(client, booked_timeslot)

    assert_success(response)

    booked_timeslot.refresh_from_db()
    assert_timeslot_is_active(booked_timeslot)


@pytest.mark.django_db
def test_unbook_timeslot_overlapping_timeslot_is_set_to_active(client,
                                                               user,
                                                               booked_timeslot,
                                                               not_active_timeslot):
    unbook_permission = Permission.objects.get(codename='delete_booking')
    user.user_permissions.add(unbook_permission)

    response = unbook_timeslot(client, booked_timeslot)

    assert_success(response)

    booked_timeslot.refresh_from_db()
    not_active_timeslot.refresh_from_db()

    assert_timeslot_is_active(booked_timeslot)
    assert_timeslot_is_active(not_active_timeslot)


def unbook_timeslot(client, timeslot):
    return client.delete(reverse('timeslot-unbook', kwargs=dict(pk=timeslot.pk)))


def assert_success(response):
    assert response.status_code == HTTP_204_NO_CONTENT


def assert_permission_denied(response):
    assert response.status_code == HTTP_403_FORBIDDEN


def assert_timeslot_unbooked(timeslot):
    assert not timeslot.booking_set.exists()
    assert not Appointment.objects.exists()


def assert_timeslot_still_booked(timeslot):
    assert timeslot.booking_set.exists()
    assert Appointment.objects.exists()


def assert_timeslot_is_active(timeslot):
    assert timeslot.active


def assert_timeslot_is_not_active(timeslot):
    assert not timeslot.active
