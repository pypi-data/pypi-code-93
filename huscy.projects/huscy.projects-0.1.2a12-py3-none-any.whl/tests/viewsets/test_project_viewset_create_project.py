import pytest
from model_bakery import baker

from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

pytestmark = pytest.mark.django_db


def test_admin_user_can_create_projects(admin_client, admin_user, research_unit):
    response = create_project(admin_client, research_unit, admin_user)

    assert response.status_code == HTTP_201_CREATED


def test_user_can_create_projects(client, user, research_unit):
    response = create_project(client, research_unit, user)

    assert response.status_code == HTTP_201_CREATED


def test_anonymous_user_cannot_create_projects(anonymous_client, user, research_unit):
    response = create_project(anonymous_client, research_unit, user)

    assert response.status_code == HTTP_403_FORBIDDEN


def test_create_project_with_existing_local_id(client, user, research_unit):
    baker.make('projects.Project', research_unit=research_unit, local_id=166)
    response = create_project(client, research_unit, user, local_id=166)

    assert response.status_code == HTTP_400_BAD_REQUEST
    error_msg = response.json()['non_field_errors']
    assert error_msg == ['The fields local_id, research_unit must make a unique set.']


def create_project(client, research_unit, principal_investigator=None, local_id=None):
    data = dict(
        description='project_description',
        principal_investigator=principal_investigator.pk,
        research_unit=research_unit.id,
        title='project_title',
    )
    if local_id:
        data['local_id'] = local_id

    return client.post(reverse('project-list'), data=data)
