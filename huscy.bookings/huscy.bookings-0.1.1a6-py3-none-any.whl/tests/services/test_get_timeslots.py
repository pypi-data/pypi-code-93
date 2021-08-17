from itertools import cycle
from datetime import datetime

import pytest
from model_bakery import baker

from huscy.bookings.services import get_timeslots

pytestmark = pytest.mark.django_db


@pytest.fixture
def projects():
    return baker.make('projects.Project', _quantity=2)


@pytest.fixture
def experiments(projects):
    return baker.make('projects.Experiment', project=cycle([projects[0], projects[0], projects[1]]),
                      _quantity=3)


@pytest.fixture
def sessions(experiments):
    return baker.make('projects.Session', experiment=cycle(experiments), _quantity=3)


@pytest.fixture
def timeslots(sessions):
    start = [datetime(2000, 12, 24, i) for i in range(10, 14)]
    return [
        baker.make('bookings.Timeslot', session=sessions[0], start=cycle(start), _quantity=2),
        baker.make('bookings.Timeslot', session=sessions[1], start=cycle(start), _quantity=3),
        baker.make('bookings.Timeslot', session=sessions[2], start=cycle(start), _quantity=4),
    ]


@pytest.mark.freeze_time('2000-12-24T08:00')
def test_get_timeslots_for_project(projects, timeslots):
    assert 5 == len(get_timeslots(projects[0]))
    assert 4 == len(get_timeslots(projects[1]))


@pytest.mark.freeze_time('2000-12-24T08:00')
def test_get_timeslots_for_experiment(projects, experiments, timeslots):
    assert 2 == len(get_timeslots(projects[0], experiments[0]))
    assert 3 == len(get_timeslots(projects[0], experiments[1]))
    assert 4 == len(get_timeslots(projects[1], experiments[2]))
    assert 0 == len(get_timeslots(projects[1], experiments[0]))


@pytest.mark.parametrize("current_time,expected_result_count", [
    (datetime(2000, 12, 24, 9), 5),
    (datetime(2000, 12, 24, 10), 5),
    (datetime(2000, 12, 24, 11), 3),
    (datetime(2000, 12, 24, 12), 1),
    (datetime(2000, 12, 24, 13), 0),
])
def test_filter_timeslots_beginning_in_the_past(freezer, projects, timeslots,
                                                current_time, expected_result_count):
    freezer.move_to(current_time)
    assert expected_result_count == len(get_timeslots(projects[0]))
