from itertools import cycle

import pytest
from model_bakery import baker

from huscy.projects.services import get_experiments

pytestmark = pytest.mark.django_db


@pytest.fixture
def experiments():
    projects = baker.make('projects.Project', _quantity=3)
    return baker.make('projects.Experiment', project=cycle(projects), _quantity=6)


def test_get_experiments(experiments):
    result = get_experiments()

    assert list(result) == experiments


def test_get_experiments_filtered_by_project(experiments):
    result = get_experiments(experiments[0].project)

    assert len(result) == 2
    assert list(result) == [experiments[0], experiments[3]]
