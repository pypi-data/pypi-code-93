from datetime import datetime, timedelta

import pytest
from model_bakery import baker


@pytest.mark.parametrize("setup_time, duration, teardown_time, expected_end", [
    (timedelta(hours=0), timedelta(hours=4), timedelta(hours=0), datetime(2000, 1, 1, 16)),
    (timedelta(hours=1), timedelta(hours=4), timedelta(hours=0), datetime(2000, 1, 1, 17)),
    (timedelta(hours=0), timedelta(hours=4), timedelta(hours=1), datetime(2000, 1, 1, 17)),
    (timedelta(hours=1), timedelta(hours=4), timedelta(hours=1), datetime(2000, 1, 1, 18)),
])
def test_end_property(setup_time, duration, teardown_time, expected_end):
    session = baker.prepare('projects.Session', duration=duration,
                            setup_time=setup_time, teardown_time=teardown_time)
    timeslot = baker.prepare('bookings.Timeslot', session=session, start=datetime(2000, 1, 1, 12))

    assert timeslot.end == expected_end


@pytest.mark.django_db
def test_has_booking_when_timeslot_is_booked(booked_timeslot):
    assert booked_timeslot.has_booking is True


@pytest.mark.django_db
def test_has_booking_whin_timeslot_is_not_booked(timeslot):
    assert timeslot.has_booking is False


@pytest.mark.django_db
@pytest.mark.parametrize("start, duration, location, has_overlap", [
    # 06:00 - 08:00 / timeslot is before booked one
    (datetime(2000, 1, 1, 6), timedelta(hours=2), 'C206', False),
    (datetime(2000, 1, 1, 6), timedelta(hours=2), 'A110', False),
    # 17:00 - 19:00 / timeslot is after booked one
    (datetime(2000, 1, 1, 17), timedelta(hours=2), 'C206', False),
    (datetime(2000, 1, 1, 17), timedelta(hours=2), 'A110', False),

    # 10:00 - 12:00 / timeslot end equals to booked start
    (datetime(2000, 1, 1, 10), timedelta(hours=2), 'C206', False),
    (datetime(2000, 1, 1, 10), timedelta(hours=2), 'A110', False),
    # 14:30 - 16:30 / timeslot start equals to booked end
    (datetime(2000, 1, 1, 14, 30), timedelta(hours=2), 'C206', False),
    (datetime(2000, 1, 1, 14, 30), timedelta(hours=2), 'A110', False),

    # 11:00 - 13:00 / timeslot overlaps booked start
    (datetime(2000, 1, 1, 11), timedelta(hours=2), 'C206', True),
    (datetime(2000, 1, 1, 11), timedelta(hours=2), 'A110', False),
    # 14:00 - 16:00 / timeslot overlaps booked end
    (datetime(2000, 1, 1, 14), timedelta(hours=2), 'C206', True),
    (datetime(2000, 1, 1, 14), timedelta(hours=2), 'A110', False),

    # 12:00 - 14:00 / timeslot start equals to booked start
    (datetime(2000, 1, 1, 12), timedelta(hours=2), 'C206', True),
    (datetime(2000, 1, 1, 12), timedelta(hours=2), 'A110', False),
    # 12:30 - 14:30 / timeslot end equals to booked end
    (datetime(2000, 1, 1, 12, 30), timedelta(hours=2), 'C206', True),
    (datetime(2000, 1, 1, 12, 30), timedelta(hours=2), 'A110', False),

    # 12:00 - 14:30 / timeslot equals with booked one
    (datetime(2000, 1, 1, 12), timedelta(hours=2, minutes=30), 'C206', True),
    (datetime(2000, 1, 1, 12), timedelta(hours=2, minutes=30), 'A110', False),

    # 13:00 - 14:00 / timeslot is between booked start and end
    (datetime(2000, 1, 1, 13), timedelta(hours=1), 'C206', True),
    (datetime(2000, 1, 1, 13), timedelta(hours=1), 'A110', False),
    # 11:00 - 15:00 / timeslot starts before and ends after booked one
    (datetime(2000, 1, 1, 11), timedelta(hours=4), 'C206', True),
    (datetime(2000, 1, 1, 11), timedelta(hours=4), 'A110', False),

    # 12:00 - 15:00 / timeslot start equals to booked start but ends after booked end
    (datetime(2000, 1, 1, 12), timedelta(hours=3), 'C206', True),
    (datetime(2000, 1, 1, 12), timedelta(hours=3), 'A110', False),
    # 11:00 - 14:30 / timeslot end equals to booked end but starts before booked start
    (datetime(2000, 1, 1, 11), timedelta(hours=3, minutes=30), 'C206', True),
    (datetime(2000, 1, 1, 11), timedelta(hours=3, minutes=30), 'A110', False),
])
def test_has_overlap_with_booked_timeslots(booked_timeslot, start, duration, location, has_overlap):
    """ the booked_timeslot is booked from 12:00 to 14:30 in room C206"""
    session = baker.make('projects.Session', duration=duration)
    baker.make('projects.DataAcquisitionMethod', session=session, location=location)
    timeslot = baker.make('bookings.Timeslot', session=session, start=start)

    assert has_overlap == timeslot.has_overlap_with_booked_timeslots()
