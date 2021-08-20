import logging

from znth.chain import Processor
from znth.command.client import ClientActiveCommand
from znth.command.project import ProjectExistCommand, ProjectActivateCommand, ProjectNotExistCommand, \
    ProjectCreateCommand, ProjectReadCommand, ProjectUpdateCommand, ProjectDeleteCommand, ProjectListCommand
from znth.factory.default import DefaultFactory


class ProjectFactory(DefaultFactory):
    log_level = logging.INFO

    @classmethod
    def create_activate(cls, level = logging.ERROR) -> Processor:
        project = cls.create_default(level)
        project.validating.append(ClientActiveCommand())
        project.validating.append(ProjectExistCommand())
        project.processing.append(ProjectActivateCommand())

        return project

    @classmethod
    def create_create(cls, level = logging.ERROR) -> Processor:
        project = cls.create_default(level)
        project.validating.append(ClientActiveCommand())
        project.validating.append(ProjectNotExistCommand())
        project.processing.append(ProjectCreateCommand())

        return project

    @classmethod
    def create_read(cls, level = logging.ERROR) -> Processor:
        project = cls.create_default(level)
        project.validating.append(ClientActiveCommand())
        project.validating.append(ProjectExistCommand())
        project.processing.append(ProjectReadCommand())

        return project

    @classmethod
    def create_update(cls, level = logging.ERROR) -> Processor:
        project = cls.create_default(level)
        project.validating.append(ClientActiveCommand())
        project.validating.append(ProjectExistCommand())
        project.processing.append(ProjectUpdateCommand())

        return project

    @classmethod
    def create_delete(cls, level = logging.ERROR) -> Processor:
        project = cls.create_default(level)
        project.validating.append(ClientActiveCommand())
        project.validating.append(ProjectExistCommand())
        project.processing.append(ProjectDeleteCommand())

        return project

    @classmethod
    def create_list(cls, level = logging.ERROR) -> Processor:
        project = cls.create_default(level)
        project.validating.append(ClientActiveCommand())
        project.processing.append(ProjectListCommand())

        return project
