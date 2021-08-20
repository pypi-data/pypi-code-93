from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_403_FORBIDDEN

from django.contrib.auth.models import Permission


def test_admin_user_can_create_research_units(admin_client, user):
    response = create_research_unit(admin_client, user)

    assert response.status_code == HTTP_201_CREATED


def test_user_with_permission_can_create_research_units(client, user):
    create_permission = Permission.objects.get(codename='add_researchunit')
    user.user_permissions.add(create_permission)

    response = create_research_unit(client, user)

    assert response.status_code == HTTP_201_CREATED, response.json()


def test_user_without_permission_cannot_create_research_units(client, user):
    response = create_research_unit(client, user)

    assert response.status_code == HTTP_403_FORBIDDEN


def test_anonymous_user_cannot_create_research_units(anonymous_client, user):
    response = create_research_unit(anonymous_client, user)

    assert response.status_code == HTTP_403_FORBIDDEN


def create_research_unit(client, user):
    return client.post(
        reverse('researchunit-list'),
        data=dict(name='research_unit_1', code='RU1', principal_investigator=user.pk)
    )
