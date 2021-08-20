from itertools import cycle

from model_bakery import baker

from huscy.projects.services import get_memberships


def test_get_memberships(django_user_model):
    projects = baker.make('projects.Project', _quantity=3)
    users = baker.make(django_user_model, _quantity=3)
    baker.make('projects.Membership', project=cycle(projects), user=cycle(users), _quantity=3)

    memberships = get_memberships()

    assert len(memberships) == 3


def test_get_memberships_filtered_by_project(django_user_model):
    projects = baker.make('projects.Project', _quantity=3)
    users = baker.make(django_user_model, _quantity=3)
    baker.make('projects.Membership', project=cycle(projects), user=cycle(users), _quantity=3)

    project = projects[0]
    memberships = get_memberships(project)

    assert len(memberships) == 1
    assert project == memberships[0].project
