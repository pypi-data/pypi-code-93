import pytest

from huscy.bookings.serializers import TimeslotSerializer

pytestmark = pytest.mark.django_db


def test_expose_session_title(timeslot):
    result = TimeslotSerializer(timeslot).data

    assert result['session_title'] == timeslot.session.title
