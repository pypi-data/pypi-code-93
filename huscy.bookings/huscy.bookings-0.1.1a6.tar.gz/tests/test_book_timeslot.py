import pytest
from model_bakery import baker

from django.contrib.auth.models import Permission

from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from huscy.appointments.models import Appointment


@pytest.fixture
def c206():
    return baker.make('appointments.Resource', name='C206')


@pytest.mark.django_db
def test_admin_user_can_book_timeslots(admin_client, timeslot, c206):
    response = book_timeslot(admin_client, timeslot)

    assert_success(response)
    assert_timeslot_booked(timeslot)
    assert_active_flag_is_false(response, timeslot)


@pytest.mark.django_db
def test_user_with_permission_can_book_timeslots(client, user, timeslot, c206):
    book_permission = Permission.objects.get(codename='add_booking')
    user.user_permissions.add(book_permission)

    response = book_timeslot(client, timeslot)

    assert_success(response)
    assert_timeslot_booked(timeslot)
    assert_active_flag_is_false(response, timeslot)


@pytest.mark.django_db
def test_user_without_permission_cannot_book_timeslots(client, timeslot):
    response = book_timeslot(client, timeslot)

    assert_permission_denied(response)
    assert_timeslot_still_unbooked(timeslot)
    assert_active_flag_is_true(response, timeslot)


@pytest.mark.django_db
def test_anonymous_user_cannot_book_timeslots(client, timeslot):
    client.logout()

    response = book_timeslot(client, timeslot)

    assert_permission_denied(response)
    assert_timeslot_still_unbooked(timeslot)
    assert_active_flag_is_true(response, timeslot)


@pytest.mark.django_db
def test_book_inactive_timeslot(client, user, timeslot):
    book_permission = Permission.objects.get(codename='add_booking')
    user.user_permissions.add(book_permission)

    timeslot.active = False
    timeslot.save()

    response = book_timeslot(client, timeslot)

    assert_bad_request(response)
    assert_error_message(response, 'Only active timeslots can be booked')
    assert_timeslot_still_unbooked(timeslot)


@pytest.mark.django_db
def test_book_timeslot_with_booked_timeslot(client, user, booked_timeslot):
    book_permission = Permission.objects.get(codename='add_booking')
    user.user_permissions.add(book_permission)

    booked_timeslot.active = True
    booked_timeslot.save()
    booked_timeslot.session.max_number_of_participants = 2
    booked_timeslot.session.save()

    response = book_timeslot(client, booked_timeslot)

    assert_success(response)
    assert booked_timeslot.booking_set.count() == 1
    assert Appointment.objects.count() == 1
    assert_active_flag_is_false(response, booked_timeslot)


@pytest.mark.django_db
def test_book_timeslot_and_max_number_of_participants_not_reached(client, user, booked_timeslot):
    book_permission = Permission.objects.get(codename='add_booking')
    user.user_permissions.add(book_permission)

    booked_timeslot.active = True
    booked_timeslot.save()
    booked_timeslot.session.max_number_of_participants = 5
    booked_timeslot.session.save()

    response = book_timeslot(client, booked_timeslot)

    assert_success(response)
    assert_active_flag_is_true(response, booked_timeslot)


def book_timeslot(client, timeslot):
    return client.post(reverse('timeslot-book', kwargs=dict(pk=timeslot.pk)))


def assert_success(response):
    assert response.status_code == HTTP_201_CREATED


def assert_bad_request(response):
    assert response.status_code == HTTP_400_BAD_REQUEST


def assert_permission_denied(response):
    assert response.status_code == HTTP_403_FORBIDDEN


def assert_error_message(response, msg):
    assert response.json() == [msg]


def assert_timeslot_booked(timeslot):
    assert timeslot.has_booking
    assert Appointment.objects.exists()


def assert_timeslot_still_unbooked(timeslot):
    assert not timeslot.has_booking
    assert not Appointment.objects.exists()


def assert_active_flag_is_false(response, timeslot):
    assert response.json()['active'] is False
    timeslot.refresh_from_db()
    assert timeslot.active is False


def assert_active_flag_is_true(response, timeslot):
    if response.status_code == HTTP_201_CREATED:
        assert response.json()['active'] is True
    timeslot.refresh_from_db()
    assert timeslot.active is True
