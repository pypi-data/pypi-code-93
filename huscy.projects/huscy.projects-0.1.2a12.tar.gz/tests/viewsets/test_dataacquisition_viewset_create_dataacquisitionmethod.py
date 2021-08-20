import pytest

from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_403_FORBIDDEN

from huscy.projects import services

pytestmark = pytest.mark.django_db


def test_admin_user_can_create_data_acquisition_methods(admin_client, session):
    response = create_data_acquisition_method(admin_client, session)

    assert response.status_code == HTTP_201_CREATED


def test_user_without_permission_can_create_data_acquisition_methods(client, session):
    response = create_data_acquisition_method(client, session)

    assert response.status_code == HTTP_201_CREATED


def test_anonymous_user_cannot_create_data_acquisition_methods(anonymous_client, session):
    response = create_data_acquisition_method(anonymous_client, session)

    assert response.status_code == HTTP_403_FORBIDDEN


@pytest.mark.skip
def test_service_function_was_called(mocker, client, session):
    spy = mocker.spy(services, 'add_data_acquisition_method')

    create_data_acquisition_method(client, session)

    spy.assert_called_once_with(session, 'eeg', 'C206', 1)


def create_data_acquisition_method(client, session):
    return client.post(
        reverse('dataacquisitionmethod-list'),
        data=dict(session=session.id, order=1, type='eeg', location='C206')
    )
