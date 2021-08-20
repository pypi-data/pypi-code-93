import pytest

from huscy.projects.services import update_membership

pytestmark = pytest.mark.django_db


def test_update_membership_make_user_to_coordinator(membership):
    assert not membership.user.has_perm('change_project', membership.project)

    update_membership(membership, is_coordinator=True, has_write_permission=True)

    assert membership.user.has_perm('change_project', membership.project)
    membership.refresh_from_db()
    assert membership.is_coordinator is True


def test_update_membership_ignores_write_permission_flag_if_is_coordinator_is_true(membership):
    assert not membership.user.has_perm('change_project', membership.project)

    update_membership(membership, is_coordinator=True, has_write_permission=False)

    assert membership.user.has_perm('change_project', membership.project)


def test_update_membership_set_write_permission(membership):
    assert not membership.user.has_perm('change_project', membership.project)

    update_membership(membership, is_coordinator=False, has_write_permission=True)

    assert membership.user.has_perm('change_project', membership.project)
    membership.refresh_from_db()
    assert membership.is_coordinator is False


def test_update_membership_remove_write_permission(membership):
    assert not membership.user.has_perm('change_project', membership.project)

    update_membership(membership, is_coordinator=False, has_write_permission=False)

    assert not membership.user.has_perm('change_project', membership.project)
    membership.refresh_from_db()
    assert membership.is_coordinator is False
