import pytest

from huscy.projects.services import add_data_acquisition_method

pytestmark = pytest.mark.django_db


def test_with_order_attribute(data_acquisition_method):
    session = data_acquisition_method.session
    method = add_data_acquisition_method(session, 'eeg', 'location', order=5)

    assert method.session == session
    assert method.type == 'eeg'
    assert method.location == 'location'
    assert method.order == 5


def test_without_order_attribute(data_acquisition_method):
    session = data_acquisition_method.session
    method = add_data_acquisition_method(session, 'eeg', 'location')

    assert method.session == session
    assert method.type == 'eeg'
    assert method.location == 'location'
    assert method.order == 2
