import pytest
from model_bakery import baker

from rest_framework.reverse import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_403_FORBIDDEN,
    HTTP_405_METHOD_NOT_ALLOWED,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def member(django_user_model):
    return baker.make(django_user_model)


def test_retrieve_membership_is_not_provided(client, project, membership):
    response = client.get(
        reverse('membership-detail', kwargs=dict(project_pk=project.pk, pk=membership.pk))
    )

    assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED


def test_admin_user_can_create_memberships(admin_client, project, member):
    response = create_membership(admin_client, project, member)

    assert response.status_code == HTTP_201_CREATED


def test_admin_user_can_delete_memberships(admin_client, project, membership):
    response = delete_membership(admin_client, project, membership)

    assert response.status_code == HTTP_204_NO_CONTENT


def test_admin_user_can_list_memberships(admin_client, project):
    response = list_memberships(admin_client, project)

    assert response.status_code == HTTP_200_OK


def test_admin_user_can_update_memberships(admin_client, project, membership):
    response = update_membership(admin_client, project, membership)

    assert response.status_code == HTTP_200_OK


@pytest.mark.parametrize('is_coordinator,expected_status_code', [
    (True, HTTP_201_CREATED),
    (False, HTTP_403_FORBIDDEN),
])
def test_create_membership_when_user_has_membership(client, user, project, member,
                                                    is_coordinator, expected_status_code):
    baker.make('projects.Membership', project=project, user=user, is_coordinator=is_coordinator)

    response = create_membership(client, project, member)

    assert response.status_code == expected_status_code


def test_user_without_membership_cannot_create_memberships(client, user, project, member):
    response = create_membership(client, project, member)

    assert response.status_code == HTTP_403_FORBIDDEN


@pytest.mark.parametrize('is_coordinator,expected_status_code', [
    (True, HTTP_204_NO_CONTENT),
    (False, HTTP_403_FORBIDDEN),
])
def test_delete_membership_with_project_membership(client, user, project, membership,
                                                   is_coordinator, expected_status_code):
    baker.make('projects.Membership', project=project, user=user, is_coordinator=is_coordinator)

    response = delete_membership(client, project, membership)

    assert response.status_code == expected_status_code


def test_user_without_membership_cannot_delete_memberships(client, user, project, membership):
    response = delete_membership(client, project, membership)

    assert response.status_code == HTTP_403_FORBIDDEN


def test_user_without_membership_can_list_memberships(client, project):
    response = list_memberships(client, project)

    assert response.status_code == HTTP_200_OK


@pytest.mark.parametrize('is_coordinator,expected_status_code', [
    (True, HTTP_200_OK),
    (False, HTTP_403_FORBIDDEN),
])
def test_update_membership_with_project_membership(client, user, project, membership,
                                                   is_coordinator, expected_status_code):
    baker.make('projects.Membership', project=project, user=user, is_coordinator=is_coordinator)

    response = update_membership(client, project, membership)

    assert response.status_code == expected_status_code


def test_user_without_membership_can_update_memberships(client, user, project, membership):
    response = update_membership(client, project, membership)

    assert response.status_code == HTTP_403_FORBIDDEN


def test_anonymous_user_cannot_create_memberships(anonymous_client, project, member):
    response = create_membership(anonymous_client, project, member)

    assert response.status_code == HTTP_403_FORBIDDEN


def test_anonymous_user_cannot_delete_memberships(anonymous_client, project, membership):
    response = delete_membership(anonymous_client, project, membership)

    assert response.status_code == HTTP_403_FORBIDDEN


def test_anonymous_user_cannot_list_memberships(anonymous_client, project):
    response = list_memberships(anonymous_client, project)

    assert response.status_code == HTTP_403_FORBIDDEN


def test_anonymous_user_cannot_update_memberships(anonymous_client, project, membership):
    response = update_membership(anonymous_client, project, membership)

    assert response.status_code == HTTP_403_FORBIDDEN


def create_membership(client, project, member, is_coordinator=False):
    return client.post(
        reverse('membership-list', kwargs=dict(project_pk=project.pk)),
        data=dict(user=member.id, is_coordinator=is_coordinator)
    )


def delete_membership(client, project, membership):
    return client.delete(
        reverse('membership-detail', kwargs=dict(project_pk=project.pk, pk=membership.id))
    )


def list_memberships(client, project):
    return client.get(reverse('membership-list', kwargs=dict(project_pk=project.pk)))


def update_membership(client, project, membership):
    return client.put(
        reverse('membership-detail', kwargs=dict(project_pk=project.pk, pk=membership.id)),
        data=dict(
            user=membership.user.id,
            is_coordinator=False,
            has_write_permission=True,
        ),
    )
