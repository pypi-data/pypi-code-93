from datetime import timedelta

import pytest
from model_bakery import baker

from huscy.projects.services import create_session


@pytest.fixture
def duration():
    return timedelta(hours=1)


def test_create_session(user, experiment, duration):
    session = create_session(experiment, duration, user)

    assert session.experiment == experiment
    assert session.duration == duration
    assert session.operator == user
    assert session.order == 1
    assert session.title == 'Session 1'


def test_create_session_to_existing_ones(user, experiment, duration):
    baker.make('projects.Session', experiment=experiment, _quantity=2)

    session = create_session(experiment, duration, user)

    assert session.order == 3
    assert session.title == 'Session 3'


def test_create_session_to_second_experiment(user, experiment, duration):
    baker.make('projects.Session', experiment=experiment, _quantity=2)
    second_experiment = baker.make('projects.Experiment', project=experiment.project)

    session = create_session(second_experiment, duration, user)

    assert session.order == 1
    assert session.title == 'Session 3'


def test_create_session_with_title(user, experiment, duration):
    session = create_session(experiment, duration, user, title='new session')

    assert session.title == 'new session'


def test_create_session_with_order(user, experiment, duration):
    session = create_session(experiment, duration, user, order=5)

    assert session.order == 5
