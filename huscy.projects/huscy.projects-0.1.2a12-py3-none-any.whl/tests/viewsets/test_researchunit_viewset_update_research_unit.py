import pytest

from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN

from django.contrib.auth.models import Permission

pytestmark = pytest.mark.django_db


def test_admin_user_can_update_research_units(admin_client, admin_user, research_unit):
    response = update_research_unit(admin_client, research_unit, admin_user)

    assert response.status_code == HTTP_200_OK
    assert_research_unit_is_updated(research_unit)


def test_admin_user_can_partial_update_research_units(admin_client, research_unit):
    response = partial_update_research_unit(admin_client, research_unit)

    assert response.status_code == HTTP_200_OK
    assert_research_unit_is_updated(research_unit)


def test_user_with_permission_can_update_research_units(client, user, research_unit):
    update_permission = Permission.objects.get(codename='change_researchunit')
    user.user_permissions.add(update_permission)

    response = update_research_unit(client, research_unit, user)

    assert response.status_code == HTTP_200_OK
    assert_research_unit_is_updated(research_unit)


def test_user_with_permission_can_partial_update_research_units(client, user, research_unit):
    update_permission = Permission.objects.get(codename='change_researchunit')
    user.user_permissions.add(update_permission)

    response = partial_update_research_unit(client, research_unit)

    assert response.status_code == HTTP_200_OK
    assert_research_unit_is_updated(research_unit)


def test_user_without_permission_cannot_update_research_units(client, user, research_unit):
    response = update_research_unit(client, research_unit, user)

    assert response.status_code == HTTP_403_FORBIDDEN
    assert_research_unit_did_not_change(research_unit)


def test_user_without_permission_cannot_partial_update_research_units(client, research_unit):
    response = partial_update_research_unit(client, research_unit)

    assert response.status_code == HTTP_403_FORBIDDEN
    assert_research_unit_did_not_change(research_unit)


def test_anonymous_user_cannot_update_research_units(anonymous_client, user, research_unit):
    response = update_research_unit(anonymous_client, research_unit, user)

    assert response.status_code == HTTP_403_FORBIDDEN
    assert_research_unit_did_not_change(research_unit)


def test_anonymous_user_cannot_partial_update_research_units(anonymous_client, research_unit):
    response = partial_update_research_unit(anonymous_client, research_unit)

    assert response.status_code == HTTP_403_FORBIDDEN
    assert_research_unit_did_not_change(research_unit)


def update_research_unit(client, research_unit, principal_investigator):
    return client.put(
        reverse('researchunit-detail', kwargs=dict(pk=research_unit.id)),
        data=dict(
            name='research_unit_2',
            code='RU2',
            principal_investigator=principal_investigator.pk
        )
    )


def partial_update_research_unit(client, research_unit):
    return client.patch(
        reverse('researchunit-detail', kwargs=dict(pk=research_unit.id)),
        data=dict(name='research_unit_2', code='RU2')
    )


def assert_research_unit_is_updated(research_unit):
    research_unit.refresh_from_db()
    assert 'research_unit_2' == research_unit.name


def assert_research_unit_did_not_change(research_unit):
    research_unit.refresh_from_db()
    assert 'research_unit_1' == research_unit.name
