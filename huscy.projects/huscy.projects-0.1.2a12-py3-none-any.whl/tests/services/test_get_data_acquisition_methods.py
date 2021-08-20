from itertools import cycle

import pytest
from model_bakery import baker

from huscy.projects.services import get_data_acquisition_methods

pytestmark = pytest.mark.django_db


@pytest.fixture
def data_acquisition_methods():
    projects = baker.make('projects.Project', _quantity=2)
    experiments = baker.make('projects.Experiment', project=cycle(projects), _quantity=2)
    sessions = baker.make('projects.Session', experiment=cycle(experiments), _quantity=2)
    return baker.make('projects.DataAcquisitionMethod', session=cycle(sessions), _quantity=4)


def test_get_data_acquisition_methods(data_acquisition_methods):
    result = get_data_acquisition_methods()

    assert len(result) == 4
    assert list(result) == data_acquisition_methods


def test_get_data_acquisition_methods_filtered_by_project(data_acquisition_methods):
    project = data_acquisition_methods[0].session.experiment.project

    result = get_data_acquisition_methods(project)

    assert len(result) == 2
    assert list(result) == [data_acquisition_methods[0], data_acquisition_methods[2]]
