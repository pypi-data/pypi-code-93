from model_bakery import baker

from huscy.projects.models import Membership, Project
from huscy.projects.services import create_project


def test_creator_is_principal_investigator(user, research_unit):
    project = create_project('title', research_unit, user, user)

    assert Project.objects.exists()
    assert Membership.objects.count() == 1
    assert Membership.objects.filter(user=user, is_coordinator=True).exists()
    assert project.description == ''
    assert user.has_perm('change_project', project)


def test_creator_is_not_principal_investigator(django_user_model, user, research_unit):
    principal_investigator = baker.make(django_user_model)
    project = create_project('title', research_unit, principal_investigator, creator=user)

    assert Project.objects.exists()
    assert Membership.objects.count() == 2
    assert Membership.objects.filter(user=user, is_coordinator=True).exists()
    assert Membership.objects.filter(user=principal_investigator, is_coordinator=True).exists()
    assert project.description == ''
    assert user.has_perm('change_project', project)
    assert principal_investigator.has_perm('change_project', project)


def test_with_optional_description(user, research_unit):
    project = create_project('title', research_unit, user, user, description='description')

    assert Project.objects.exists()
    assert not project.description == ''


def test_with_optional_local_id(user, research_unit):
    project = create_project('title', research_unit, user, user, local_id=166)
    assert Project.objects.exists()
    assert project.local_id == 166
