from operator import attrgetter

import pytest
from model_bakery import baker

from huscy.projects.services import get_projects

pytestmark = pytest.mark.django_db


@pytest.fixture
def projects():
    return baker.make('projects.Project', _quantity=10)


def test_get_projects(projects):
    result = get_projects()

    assert list(sorted(projects, key=attrgetter('id'), reverse=True)) == list(result)
