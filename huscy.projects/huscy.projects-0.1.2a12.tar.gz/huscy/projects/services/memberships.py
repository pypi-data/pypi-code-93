from django.db.models import Q

from guardian.shortcuts import assign_perm, remove_perm

from huscy.projects.models import Membership, Project


def add_member(project, user, is_coordinator=False, has_write_permission=False):
    assign_perm('view_project', user, project)
    if is_coordinator or has_write_permission:
        assign_perm('change_project', user, project)
    return Membership.objects.create(
        project=project,
        user=user,
        is_coordinator=is_coordinator,
    )


def get_memberships(project=None):
    qs = Membership.objects.order_by('project__id', 'user__id')
    if project:
        qs = qs.filter(project=project)
    return qs


def remove_member(membership):
    remove_perm('view_project', membership.user, membership.project)
    remove_perm('change_project', membership.user, membership.project)
    membership.delete()


def update_membership(membership, is_coordinator, has_write_permission):
    if is_coordinator or has_write_permission:
        assign_perm('change_project', membership.user, membership.project)
    else:
        remove_perm('change_project', membership.user, membership.project)
    membership.is_coordinator = is_coordinator
    membership.save()
    return membership


def get_participating_projects(user):
    return (Project.objects
                   .filter(Q(principal_investigator=user) | Q(membership__user=user))
                   .distinct())
