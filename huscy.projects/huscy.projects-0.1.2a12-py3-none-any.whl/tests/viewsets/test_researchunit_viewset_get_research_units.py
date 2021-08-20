from itertools import cycle

import pytest
from model_bakery import baker

from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN

from huscy.projects import services

pytestmark = pytest.mark.django_db


def test_get_research_units_service_function():
    names = ['Project1', 'This is a project', 'A new project']
    baker.make('projects.ResearchUnit', name=cycle(names), _quantity=len(names))

    research_units = services.get_research_units()

    assert sorted(names) == list(research_units.values_list('name', flat=True))


def test_admin_user_can_list_research_units(admin_client):
    response = list_research_unit(admin_client)

    assert response.status_code == HTTP_200_OK


def test_user_without_permission_can_list_research_units(client):
    response = list_research_unit(client)

    assert response.status_code == HTTP_200_OK


def test_anonymous_user_cannot_list_research_units(anonymous_client):
    response = list_research_unit(anonymous_client)

    assert response.status_code == HTTP_403_FORBIDDEN


def list_research_unit(client):
    return client.get(reverse('researchunit-list'))
