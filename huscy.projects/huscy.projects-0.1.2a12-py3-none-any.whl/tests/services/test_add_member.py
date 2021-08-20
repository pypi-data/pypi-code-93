import pytest

from django.db import IntegrityError

from huscy.projects.models import Membership
from huscy.projects.services import add_member


@pytest.mark.django_db
def test_add_normal_member(project, user):
    assert_membership_does_not_exist()

    add_member(project, user)

    assert_membership_exists(project, user)
    assert_user_has_view_permission_for_project(project, user)
    assert_user_does_not_have_change_permission_for_project(project, user)


@pytest.mark.django_db
def test_add_member_as_coordinator(project, user):
    assert_membership_does_not_exist()

    add_member(project, user, is_coordinator=True)

    assert_membership_exists(project, user)
    assert_user_is_coordinator(project, user)
    assert_user_has_view_permission_for_project(project, user)
    assert_user_has_change_permission_for_project(project, user)


@pytest.mark.django_db
def test_add_member_with_write_permission(project, user):
    assert_membership_does_not_exist()

    add_member(project, user, has_write_permission=True)

    assert_membership_exists(project, user)
    assert_user_is_not_coordinator(project, user)
    assert_user_has_view_permission_for_project(project, user)
    assert_user_has_change_permission_for_project(project, user)


@pytest.mark.django_db
def test_has_write_permission_is_ignored_if_is_coordinator_is_set_to_true(project, user):
    assert_membership_does_not_exist()

    add_member(project, user, is_coordinator=True, has_write_permission=False)

    assert_membership_exists(project, user)
    assert_user_is_coordinator(project, user)
    assert_user_has_view_permission_for_project(project, user)
    assert_user_has_change_permission_for_project(project, user)


@pytest.mark.django_db
def test_add_member_twice_to_project_fails(project, user):
    assert_membership_does_not_exist()

    add_member(project, user)
    with pytest.raises(IntegrityError):
        add_member(project, user)


def assert_membership_does_not_exist():
    assert not Membership.objects.exists()


def assert_membership_exists(project, user):
    membership = Membership.objects.get()
    assert membership.project == project
    assert membership.user == user


def assert_user_is_coordinator(project, user):
    membership = Membership.objects.filter(is_coordinator=True).get()
    assert membership.project == project
    assert membership.user == user


def assert_user_is_not_coordinator(project, user):
    membership = Membership.objects.filter(is_coordinator=False).get()
    assert membership.project == project
    assert membership.user == user


def assert_user_has_view_permission_for_project(project, user):
    assert user.has_perm('view_project', project)


def assert_user_has_change_permission_for_project(project, user):
    assert user.has_perm('change_project', project)


def assert_user_does_not_have_change_permission_for_project(project, user):
    assert not user.has_perm('change_project', project)
