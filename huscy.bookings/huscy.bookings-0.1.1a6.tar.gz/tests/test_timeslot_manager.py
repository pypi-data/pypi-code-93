from datetime import datetime, timedelta

import pytest
from model_bakery import baker

from huscy.bookings.models import Timeslot


@pytest.mark.django_db
def test_get_overlapping_timeslots(timeslot):
    timeslots = list(create_timeslots())

    # exclude timeslot 1 because it's self
    # exclude timeslots 2 - 40 because they take place in room A110
    # exclude timeslots 41 - 45 and 54 - 55 because they are before self
    # exclude timeslots 52, 53, 65, 66, 78 and 79 because they are after self
    expected_overlapping_timeslots = timeslots[44:50] + timeslots[54:63] + timeslots[65:76]

    overlapping_timeslots = Timeslot.objects.get_overlapping_timeslots(timeslot)
    assert list(overlapping_timeslots) == expected_overlapping_timeslots


@pytest.mark.django_db
def test_set_overlapping_timeslots_inactive(timeslot):
    create_timeslots()

    Timeslot.objects.set_overlapping_timeslots_inactive(timeslot)

    assert_overlapping_timeslots_are_inactive(timeslot)


def create_timeslots():
    """
    This function creates timeslots in rooms A110 and C206. For each room, there are sessions that
    lasts one, two and a half and four hours. For every duration there's a start time from 09:00
    to 15:00 every half an hour.
    The table below lists the timeslots with their database id and start and end time.

    Duration:   one hour                two and a half hours    four hours
    Room A110    2 - 09:00-10:00        15 - 09:00-11:30        28 - 09:00-13:00
                 3 - 09:30-10:30        16 - 09:30-12:00        29 - 09:30-13:30
                 4 - 10:00-11:00        17 - 10:00-12:30        30 - 10:00-14:00
                             ...                     ...                     ...
                12 - 14:00-15:00        25 - 14:00-16:30        38 - 14:00-18:00
                13 - 14:30-15:30        26 - 14:30-17:00        39 - 14:30-18:30
                14 - 15:00-16:00        27 - 15:00-17:30        40 - 15:00-19:00

    Room C206   41 - 09:00-10:00        54 - 09:00-11:30        67 - 09:00-13:00
                42 - 09:30-10:30        55 - 09:30-12:00        68 - 09:30-13:30
                43 - 10:00-11:00        56 - 10:00-12:30        69 - 10:00-14:00
                44 - 10:30-11:30        57 - 10:30-13:00        70 - 10:30-14:30
                45 - 11:00-12:00        58 - 11:00-13:30        71 - 11:00-15:00
                46 - 11:30-12:30        59 - 11:30-14:00        72 - 11:30-15:30
                             ...                     ...                     ...
                50 - 13:30-14:30        63 - 13:30-16:00        76 - 13:30-17:30
                51 - 14:00-15:00        64 - 14:00-16:30        77 - 14:00-18:00
                52 - 14:30-15:30        65 - 14:30-17:00        78 - 14:30-18:30
                53 - 15:00-16:00        66 - 15:00-17:30        79 - 15:00-19:00
    """
    for location in ['A110', 'C206']:
        for duration in [timedelta(hours=1), timedelta(hours=2, minutes=30), timedelta(hours=4)]:
            session = baker.make('projects.Session', duration=duration)
            baker.make('projects.DataAcquisitionMethod', session=session, location=location)
            start = datetime(2000, 1, 1, 9)
            for delta in [timedelta(minutes=minutes) for minutes in range(0, 6*60+1, 30)]:
                yield baker.make('bookings.Timeslot', session=session, start=start + delta)


def assert_overlapping_timeslots_are_inactive(timeslot):
    overlapping_timeslots = Timeslot.objects.get_overlapping_timeslots(timeslot)
    assert list(overlapping_timeslots) == list(Timeslot.objects.filter(active=False))
