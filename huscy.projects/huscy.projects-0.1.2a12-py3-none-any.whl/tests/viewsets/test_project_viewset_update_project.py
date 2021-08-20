import pytest
from model_bakery import baker

from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from django.contrib.auth.models import Permission

from huscy.projects.models import Project

pytestmark = pytest.mark.django_db


def test_admin_user_can_update_projects(admin_client, project):
    response = update_project(admin_client, project)

    assert response.status_code == HTTP_200_OK
    assert_project_is_updated(project)


def test_admin_user_can_partial_update_projects(admin_client, project):
    response = partial_update_project(admin_client, project)

    assert response.status_code == HTTP_200_OK
    assert_project_is_updated(project)


def test_user_with_permission_can_update_projects(client, user, project):
    update_permission = Permission.objects.get(codename='change_project')
    user.user_permissions.add(update_permission)

    response = update_project(client, project)

    assert response.status_code == HTTP_200_OK
    assert_project_is_updated(project)


def test_user_cannot_update_local_id_to_other_existing_local_id(client, user, project):
    update_permission = Permission.objects.get(codename='change_project')
    user.user_permissions.add(update_permission)
    other = baker.make('projects.Project',
                       research_unit=project.research_unit,
                       local_id=project.local_id + 1)
    response = update_project(client, project, local_id=other.local_id)

    assert response.status_code == HTTP_400_BAD_REQUEST, response.json()
    assert_project_did_not_change(project)


def test_user_can_update_local_id_to_unused_local_id(client, user, project):
    update_permission = Permission.objects.get(codename='change_project')
    user.user_permissions.add(update_permission)

    assert not Project.objects.filter(local_id=project.local_id + 1,
                                      research_unit=project.research_unit).exists()
    response = update_project(client, project, local_id=project.local_id + 1)

    assert response.status_code == HTTP_200_OK

    assert not Project.objects.filter(local_id=project.local_id,
                                      research_unit=project.research_unit).exists()


def test_user_with_permission_can_partial_update_research_units(client, user, project):
    update_permission = Permission.objects.get(codename='change_project')
    user.user_permissions.add(update_permission)

    response = partial_update_project(client, project)

    assert response.status_code == HTTP_200_OK
    assert_project_is_updated(project)


def test_user_without_permission_cannot_update_projects(client, project):
    response = update_project(client, project)

    assert response.status_code == HTTP_403_FORBIDDEN
    assert_project_did_not_change(project)


def test_user_without_permission_cannot_partial_update_projects(client, project):
    response = partial_update_project(client, project)

    assert response.status_code == HTTP_403_FORBIDDEN
    assert_project_did_not_change(project)


def test_anonymous_user_cannot_update_projects(anonymous_client, project):
    response = update_project(anonymous_client, project)

    assert response.status_code == HTTP_403_FORBIDDEN
    assert_project_did_not_change(project)


def test_anonymous_user_cannot_partial_update_projects(anonymous_client, project):
    response = partial_update_project(anonymous_client, project)

    assert response.status_code == HTTP_403_FORBIDDEN
    assert_project_did_not_change(project)


def update_project(client, project, local_id=None):
    return client.put(
        reverse('project-detail', kwargs=dict(pk=project.pk)),
        data=dict(
            description=project.description,
            principal_investigator=project.principal_investigator.id,
            research_unit=project.research_unit.pk,
            title='new_project_title',
            local_id=local_id or project.local_id,
        )
    )


def partial_update_project(client, project):
    return client.patch(
        reverse('project-detail', kwargs=dict(pk=project.pk)),
        data=dict(title='new_project_title')
    )


def assert_project_is_updated(project):
    project.refresh_from_db()
    assert 'new_project_title' == project.title


def assert_project_did_not_change(project):
    project.refresh_from_db()
    assert 'project_title' == project.title
