from rest_framework.reverse import reverse
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_403_FORBIDDEN

from django.contrib.auth.models import Permission


def test_admin_user_can_delete_research_units(admin_client, research_unit):
    response = delete_research_unit(admin_client, research_unit)

    assert response.status_code == HTTP_204_NO_CONTENT


def test_user_with_permission_can_delete_research_units(client, user, research_unit):
    create_permission = Permission.objects.get(codename='delete_researchunit')
    user.user_permissions.add(create_permission)

    response = delete_research_unit(client, research_unit)

    assert response.status_code == HTTP_204_NO_CONTENT


def test_user_without_permission_cannot_delete_research_units(client, research_unit):
    response = delete_research_unit(client, research_unit)

    assert response.status_code == HTTP_403_FORBIDDEN


def test_anonymous_user_cannot_delete_research_units(anonymous_client, research_unit):
    response = delete_research_unit(anonymous_client, research_unit)

    assert response.status_code == HTTP_403_FORBIDDEN


def delete_research_unit(client, research_unit):
    return client.delete(reverse('researchunit-detail', kwargs=dict(pk=research_unit.id)))
