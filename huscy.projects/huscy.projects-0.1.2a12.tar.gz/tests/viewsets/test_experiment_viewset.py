import pytest

from rest_framework.reverse import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_403_FORBIDDEN,
    HTTP_405_METHOD_NOT_ALLOWED,
)

pytestmark = pytest.mark.django_db


def test_retrieve_is_not_provided(client, project, experiment):
    response = client.get(
        reverse('experiment-detail', kwargs=dict(project_pk=project.pk, pk=experiment.pk))
    )

    assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED


def test_admin_user_can_create_experiments(admin_client, project):
    response = create_experiment(admin_client, project)

    assert response.status_code == HTTP_201_CREATED


def test_admin_user_can_delete_experiments(admin_client, project, experiment):
    response = delete_experiment(admin_client, project, experiment)

    assert response.status_code == HTTP_204_NO_CONTENT


def test_admin_user_can_list_experiments(admin_client, project):
    response = list_experiments(admin_client, project)

    assert response.status_code == HTTP_200_OK


def test_admin_user_can_update_experiments(admin_client, project, experiment):
    response = update_experiment(admin_client, project, experiment)

    assert response.status_code == HTTP_200_OK


def test_user_without_permission_can_create_experiments(client, project):
    response = create_experiment(client, project)

    assert response.status_code == HTTP_201_CREATED


def test_user_without_permission_can_delete_experiments(client, project, experiment):
    response = delete_experiment(client, project, experiment)

    assert response.status_code == HTTP_204_NO_CONTENT


def test_user_without_permission_can_list_experiments(client, project):
    response = list_experiments(client, project)

    assert response.status_code == HTTP_200_OK


def test_user_without_permission_can_update_experiments(client, project, experiment):
    response = update_experiment(client, project, experiment)

    assert response.status_code == HTTP_200_OK


def test_anonymous_user_cannot_create_experiments(anonymous_client, project):
    response = create_experiment(anonymous_client, project)

    assert response.status_code == HTTP_403_FORBIDDEN


def test_anonymous_user_cannot_delete_experiments(anonymous_client, project, experiment):
    response = delete_experiment(anonymous_client, project, experiment)

    assert response.status_code == HTTP_403_FORBIDDEN


def test_anonymous_user_cannot_list_experiments(anonymous_client, project):
    response = list_experiments(anonymous_client, project)

    assert response.status_code == HTTP_403_FORBIDDEN


def test_anonymous_user_cannot_update_experiments(anonymous_client, project, experiment):
    response = update_experiment(anonymous_client, project, experiment)

    assert response.status_code == HTTP_403_FORBIDDEN


def create_experiment(client, project):
    return client.post(reverse('experiment-list', kwargs=dict(project_pk=project.pk)), data={})


def delete_experiment(client, project, experiment):
    return client.delete(
        reverse('experiment-detail', kwargs=dict(project_pk=project.pk, pk=experiment.pk))
    )


def list_experiments(client, project):
    return client.get(reverse('experiment-list', kwargs=dict(project_pk=project.pk)))


def update_experiment(client, project, experiment):
    return client.put(
        reverse('experiment-detail', kwargs=dict(project_pk=project.pk, pk=experiment.pk)),
        data=dict(
            description='new description',
            order=experiment.order,
            title='new title',
        )
    )
