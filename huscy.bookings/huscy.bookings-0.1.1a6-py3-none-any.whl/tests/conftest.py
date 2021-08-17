from datetime import datetime, timedelta

from model_bakery import baker
import pytest

from rest_framework.test import APIClient


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(username='user', password='password',
                                                 first_name='Christiane', last_name='Krise')


@pytest.fixture
def client(user):
    client = APIClient()
    client.login(username=user.username, password='password')
    return client


@pytest.fixture
def admin_client(admin_user):
    client = APIClient()
    client.login(username=admin_user.username, password='password')
    return client


@pytest.fixture
def anonymous_client():
    return APIClient()


@pytest.fixture
def session():
    return baker.make(
        'projects.Session',
        duration=timedelta(hours=2),
        setup_time=timedelta(minutes=15),
        teardown_time=timedelta(minutes=15),
    )


@pytest.fixture
def data_acquisition_method(session):
    return baker.make(
        'projects.DataAcquisitionMethod',
        session=session,
        location='C206',
    )


@pytest.fixture
def timeslot(data_acquisition_method):
    """ timeslot at 2000-01-01 12:00 with a duration of two and a half hours """
    return baker.make(
        'bookings.Timeslot',
        session=data_acquisition_method.session,
        start=datetime(2000, 1, 1, 12),
    )


@pytest.fixture
def booked_timeslot():
    """ timeslot at 2000-01-01 12:00 with a duration of two and a half hours"""
    start = datetime(2000, 1, 1, 12)

    session = baker.make('projects.Session', setup_time=timedelta(minutes=15),
                         duration=timedelta(hours=2), teardown_time=timedelta(minutes=15))
    baker.make('projects.DataAcquisitionMethod', session=session, location='C206')
    timeslot = baker.make('bookings.Timeslot', session=session, start=start, active=False)
    appointment = baker.make('appointments.Appointment', start=start, end=timeslot.end,
                             resource='C206')
    baker.make('appointments.Invitation', appointment=appointment, participant='abcd')
    baker.make('bookings.Booking', timeslot=timeslot, appointment=appointment)
    return timeslot


@pytest.fixture
def not_active_timeslot(booked_timeslot):
    """ timeslot at 2000-01-01 13:00"""
    start = datetime(2000, 1, 1, 13)

    timeslot = baker.make('bookings.Timeslot', session=booked_timeslot.session,
                          start=start, active=False)
    return timeslot


@pytest.fixture
def project():
    return baker.make('projects.Project')


@pytest.fixture
def experiment(project):
    return baker.make('projects.Experiment', project=project)
