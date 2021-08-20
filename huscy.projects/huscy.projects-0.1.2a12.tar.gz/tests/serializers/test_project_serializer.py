import pytest

from huscy.projects.serializer import ProjectSerializer

pytestmark = pytest.mark.django_db


def test_project_serializer(rf, user, project):
    request = rf.get('/any/path/')
    request.user = user

    expected = dict(
        description=project.description,
        id=project.id,
        local_id=project.local_id,
        local_id_name=project.local_id_name,
        participating=False,
        principal_investigator=project.principal_investigator.pk,
        principal_investigator_name=project.principal_investigator.get_full_name(),
        research_unit=project.research_unit.pk,
        research_unit_name=project.research_unit.name,
        title=project.title,
    )

    assert expected == ProjectSerializer(instance=project, context={'request': request}).data


def test_participating_flag_with_member(rf, membership):
    request = rf.get('/any/path/')
    request.user = membership.user

    serializer = ProjectSerializer(instance=membership.project, context={'request': request})

    assert serializer.data['participating'] is True


def test_participating_flag_with_principal_investigator(rf, project):
    request = rf.get('/any/path/')
    request.user = project.principal_investigator

    serializer = ProjectSerializer(instance=project, context={'request': request})

    assert serializer.data['participating'] is True


def test_participating_flag_with_any_other_user(rf, user, project):
    request = rf.get('/any/path/')
    request.user = user

    serializer = ProjectSerializer(instance=project, context={'request': request})

    assert serializer.data['participating'] is False
