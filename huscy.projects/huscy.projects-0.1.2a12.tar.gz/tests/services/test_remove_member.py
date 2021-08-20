import pytest

from huscy.projects.models import Membership
from huscy.projects.services import add_member, remove_member

pytestmark = pytest.mark.django_db


def test_remove_membership(project, user):
    membership = add_member(project, user)  # use service function here to set the permission
    assert_user_has_view_permission_for_project(project, user)
    assert_user_does_not_have_change_permission_for_project(project, user)

    remove_member(membership)

    assert_user_does_not_have_view_permission_for_project(project, user)
    assert_user_does_not_have_change_permission_for_project(project, user)
    assert_membership_does_not_exist()


def test_write_permission_is_removed_as_well(project, user):
    membership = add_member(project, user, is_coordinator=True)  # user has write permission now
    assert_user_has_change_permission_for_project(project, user)

    remove_member(membership)

    assert_user_does_not_have_view_permission_for_project(project, user)
    assert_user_does_not_have_change_permission_for_project(project, user)
    assert_membership_does_not_exist()


def assert_membership_does_not_exist():
    assert not Membership.objects.exists()


def assert_membership_exists(project, user):
    membership = Membership.objects.get()
    assert membership.project == project
    assert membership.user == user


def assert_user_has_view_permission_for_project(project, user):
    assert user.has_perm('view_project', project)


def assert_user_does_not_have_view_permission_for_project(project, user):
    assert not user.has_perm('view_project', project)


def assert_user_has_change_permission_for_project(project, user):
    assert user.has_perm('change_project', project)


def assert_user_does_not_have_change_permission_for_project(project, user):
    assert not user.has_perm('change_project', project)
