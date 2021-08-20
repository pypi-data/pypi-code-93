import datetime
import logging

from sqlalchemy import true

from znth.chain import Command, ContextKeyException
from znth.command.database import DatabaseContext
from znth.models import Task, TaskState


class TaskActiveCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("active.execute() - Start")

        if "project" not in context:
            raise ContextKeyException("project")

        project = context["project"]
        task = context.session.query(Task).filter(Task.project_id == project.project_id, Task.task_active == true()).first()

        if task:
            context["task"] = task
            found = True
        else:
            logger.warning("No active task found")
            found = False

        logger.debug("active.execute() - Finish")
        return found


class TaskCreateCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("create.execute() - Start")

        if "project" not in context:
            raise ContextKeyException("project")

        project = context["project"]

        task = Task(project_id=project.project_id)
        context.session.add(task)

        logger.info(f"Task[task_name = NEW] - created")
        logger.debug("create.execute() - Finish")
        return Command.SUCCESS


class TaskReadCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("read.execute() - Start")

        if "task_id" not in context:
            raise ContextKeyException("task_id")

        if "project" not in context:
            raise ContextKeyException("project")

        task_id = int(context["task_id"])
        project = context["project"]

        task = context.session.query(Task).filter(Task.project_id == project.project_id, Task.task_id == task_id).one()

        context["task"] = task

        logger.debug("read.execute() - Finish")
        return Command.SUCCESS


class TaskUpdateCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("update.execute() - Start")

        if "task_id" not in context:
            raise ContextKeyException("task_id")

        if "project" not in context:
            raise ContextKeyException("project")

        updated = False
        task_id = int(context["task_id"])
        project = context["project"]

        task = context.session.query(Task).filter(Task.project_id == project.project_id, Task.task_id == task_id).one()

        if "task_name" in context:
            task.task_name = context["task_name"]
            updated = True

        if "task_active" in context:
            task.task_active = context["task_active"]
            updated = True

        if "task_description" in context:
            task.task_description = context["task_description"]
            updated = True

        if "task_remark" in context:
            task.task_remark = context["task_remark"]
            updated = True

        if updated:
            logger.info(f"Task[task_id = {task_id}] - updated")
        else:
            logger.warning(f"Task[task_id = {task_id}] - not updated")

        logger.debug("update.execute() - Finish")
        return updated


class TaskDeleteCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("delete.execute() - Start")

        if "task_id" not in context:
            raise ContextKeyException("task_id")

        if "project" not in context:
            raise ContextKeyException("project")

        task_id = int(context["task_id"])
        project = context["project"]

        task = context.session.query(Task).filter(Task.project_id == project.project_id, Task.task_id == task_id).one()
        context.session.delete(task)

        logger.info(f"Task[task_id = {task_id}] - deleted")
        logger.debug("delete.execute() - Finish")
        return Command.SUCCESS


class TaskListCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("list.execute() - Start")

        if "project" not in context:
            raise ContextKeyException("project")

        project = context["project"]

        tasks = context.session.query(Task).filter(Task.project_id == project.project_id).order_by(
            Task.task_id).all()
        context["tasks"] = tasks

        logger.debug("list.execute() - Finish")
        return Command.SUCCESS


class TaskNewCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("new.execute() - Start")

        if "project" not in context:
            raise ContextKeyException("project")

        project = context["project"]

        task = Task(project_id=project.project_id, task_state=TaskState.NEW)
        context.session.add(task)

        logger.info(f"Task[task_id = NEW] - created")
        logger.debug("new.execute() - Finish")
        return Command.SUCCESS


class TaskStartCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("start.execute() - Start")

        if "task_id" not in context:
            raise ContextKeyException("task_id")

        if "project" not in context:
            raise ContextKeyException("project")

        task_id = int(context["task_id"])
        project = context["project"]

        for task in context.session.query(Task).filter(Task.task_active == true()).all():
            task.task_active = False

        task = context.session.query(Task).filter(Task.project_id == project.project_id, Task.task_id == task_id).one()

        if task.task_state != TaskState.NEW:
            logger.warning(f"Task[task_id = {task_id}] is not NEW")
            return Command.FAILURE

        task.task_active = True
        task.task_state = TaskState.STARTED
        task.task_start = datetime.datetime.now()

        logger.info(f"Task[task_id = {task_id}] - started")
        logger.debug("start.execute() - Finish")
        return Command.SUCCESS


class TaskStopCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("stop.execute() - Start")

        if "task_id" not in context:
            raise ContextKeyException("task_id")

        if "project" not in context:
            raise ContextKeyException("project")

        project = context["project"]
        task_id = int(context["task_id"])

        task = context.session.query(Task).filter(Task.project_id == project.project_id, Task.task_id == task_id).one()

        if task.task_state != TaskState.STARTED:
            logger.warning(f"Task[task_id = {task_id}] is not STARTED")
            return Command.FAILURE

        task.task_active = False
        task.task_state = TaskState.STOPPED
        task.task_finish = datetime.datetime.now()

        difference = task.task_finish - task.task_start
        seconds = int(difference.total_seconds())
        task.task_duration = task.task_duration + seconds

        logger.info(f"Task[task_id = {task_id}] - stopped")
        logger.debug("stop.execute() - Finish")
        return Command.SUCCESS
