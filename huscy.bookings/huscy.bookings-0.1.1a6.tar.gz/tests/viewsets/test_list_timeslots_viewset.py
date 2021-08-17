import pytest

from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN

pytestmark = pytest.mark.django_db


def test_admin_can_list_timeslots_for_project(admin_client, project):
    response = list_project_timeslots(admin_client, project)

    assert response.status_code == HTTP_200_OK


def test_admin_can_list_timeslots_for_experiment(admin_client, experiment):
    response = list_experiment_timeslots(admin_client, experiment)

    assert response.status_code == HTTP_200_OK


def test_user_without_permission_can_list_timeslots_for_project(client, project):
    response = list_project_timeslots(client, project)

    assert response.status_code == HTTP_200_OK


def test_user_without_permission_can_list_timeslots_for_experiment(client, experiment):
    response = list_experiment_timeslots(client, experiment)

    assert response.status_code == HTTP_200_OK


def test_anonymous_user_cannot_list_timeslosts_for_project(anonymous_client, project):
    response = list_project_timeslots(anonymous_client, project)

    assert response.status_code == HTTP_403_FORBIDDEN


def test_anonymous_user_cannot_list_timeslots_for_experiment(anonymous_client, experiment):
    response = list_experiment_timeslots(anonymous_client, experiment)

    assert response.status_code == HTTP_403_FORBIDDEN


def list_project_timeslots(client, project):
    return client.get(reverse('project-timeslots-list', kwargs=dict(project_pk=project.pk)))


def list_experiment_timeslots(client, experiment):
    return client.get(reverse('experiment-timeslots-list', kwargs=dict(
        project_pk=experiment.project.pk, experiment_pk=experiment.pk
    )))
