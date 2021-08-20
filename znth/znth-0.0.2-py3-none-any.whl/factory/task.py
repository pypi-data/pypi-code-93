import logging

from znth.chain import Processor
from znth.command.client import ClientActiveCommand
from znth.command.project import ProjectActiveCommand
from znth.command.task import TaskNewCommand, TaskStartCommand, TaskActiveCommand, TaskStopCommand, \
    TaskListCommand, TaskReadCommand, TaskUpdateCommand, TaskDeleteCommand
from znth.factory.default import DefaultFactory


class TaskFactory(DefaultFactory):
    @classmethod
    def create_new(cls, level=logging.ERROR) -> Processor:
        task = cls.create_default(level)
        task.validating.append(ClientActiveCommand())
        task.validating.append(ProjectActiveCommand())
        task.processing.append(TaskNewCommand())

        return task

    @classmethod
    def create_start(cls, level=logging.ERROR) -> Processor:
        task = cls.create_default(level)
        task.validating.append(ClientActiveCommand())
        task.validating.append(ProjectActiveCommand())
        task.processing.append(TaskStartCommand())

        return task

    @classmethod
    def create_stop(cls, level=logging.ERROR) -> Processor:
        task = cls.create_default(level)
        task.validating.append(ClientActiveCommand())
        task.validating.append(ProjectActiveCommand())
        task.validating.append(TaskActiveCommand())
        task.processing.append(TaskStopCommand())

        return task

    @classmethod
    def create_read(cls, level=logging.ERROR) -> Processor:
        task = cls.create_default(level)
        task.validating.append(ClientActiveCommand())
        task.validating.append(ProjectActiveCommand())
        # task.validating.append(TaskActiveCommand())
        task.processing.append(TaskReadCommand())

        return task

    @classmethod
    def create_update(cls, level=logging.ERROR) -> Processor:
        task = cls.create_default(level)
        task.validating.append(ClientActiveCommand())
        task.validating.append(ProjectActiveCommand())
        task.processing.append(TaskUpdateCommand())

        return task

    @classmethod
    def create_delete(cls, level=logging.ERROR) -> Processor:
        task = cls.create_default(level)
        task.validating.append(ClientActiveCommand())
        task.validating.append(ProjectActiveCommand())
        task.processing.append(TaskDeleteCommand())

        return task

    @classmethod
    def create_list(cls, level=logging.ERROR) -> Processor:
        task = cls.create_default(level)
        task.validating.append(ClientActiveCommand())
        task.validating.append(ProjectActiveCommand())
        task.processing.append(TaskListCommand())

        return task
