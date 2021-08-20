import pytest
from model_bakery import baker

from huscy.projects.services import create_experiment

pytestmark = pytest.mark.django_db


def test_create_experiment(project):
    experiment = create_experiment(project)

    assert experiment.project == project
    assert experiment.title == 'Experiment 1'
    assert experiment.description == ''
    assert experiment.order == 1


def test_create_experiment_to_existing_ones(project):
    baker.make('projects.Experiment', project=project, _quantity=2)
    experiment = create_experiment(project)

    assert experiment.title == 'Experiment 3'
    assert experiment.order == 3


def test_create_experiment_with_title(project):
    experiment = create_experiment(project, 'the experiment')

    assert experiment.title == 'the experiment'


def test_create_experiment_with_order(project):
    experiment = create_experiment(project, order=5)

    assert experiment.order == 5
