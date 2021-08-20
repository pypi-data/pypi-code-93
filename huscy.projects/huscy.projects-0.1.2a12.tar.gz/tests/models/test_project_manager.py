import pytest
from model_bakery import baker

from huscy.projects import models

pytestmark = pytest.mark.django_db


def test_get_next_local_id_on_empty_projects(research_unit):
    assert not models.Project.objects.exists()
    assert models.Project.objects.get_next_local_id(research_unit) == 1


def test_get_next_local_id_with_one_project():
    project = baker.make('projects.Project', local_id=1)
    assert models.Project.objects.count() == 1
    assert models.Project.objects.get_next_local_id(project.research_unit) == 2


def test_get_next_local_id_with_gap_in_local_ids(research_unit):
    baker.make('projects.Project', local_id=1, research_unit=research_unit)
    baker.make('projects.Project', local_id=3, research_unit=research_unit)
    assert models.Project.objects.get_next_local_id(research_unit) == 2
