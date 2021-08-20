import logging

from django.db.transaction import atomic

from .memberships import add_member, remove_member
from huscy.projects.models import Project

logger = logging.getLogger('projects')


@atomic
def create_project(title, research_unit, principal_investigator, creator,
                   local_id=None, description=''):
    if local_id is None:
        local_id = Project.objects.get_next_local_id(research_unit)

    project = Project.objects.create(
        description=description,
        local_id=local_id,
        principal_investigator=principal_investigator,
        research_unit=research_unit,
        title=title,
    )
    logger.info('Project id:%d, local_id_name:%s, title:%s reserch_unit:%s has been created',
                project.id, project.local_id_name, project.title, project.research_unit.name)

    add_member(project, principal_investigator, is_coordinator=True)
    if principal_investigator != creator:
        add_member(project, creator, is_coordinator=True)

    return project


@atomic
def delete_project(project):
    map(remove_member, project.membership_set.all())
    logger.info('All members from project <id: %d> removed', project.id)

    project.delete()
    logger.info('Project id:%d, local_id_name:%s, title:%s research_unit:%s has been deleted',
                project.id, project.local_id_name, project.title, project.research_unit.name)


def get_projects():
    return Project.objects.all()
