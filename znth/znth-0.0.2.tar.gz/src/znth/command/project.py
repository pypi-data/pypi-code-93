import logging

from sqlalchemy import true

from znth.chain import Command, ContextKeyException
from znth.command.database import DatabaseContext
from znth.models import Project


class ProjectActivateCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("activate.execute() - Start")

        if "project_name" not in context:
            raise ContextKeyException("project_name")

        project_name = context["project_name"]

        for project in context.session.query(Project).filter(Project.project_active == true()).all():
            project.project_active = False

        project = context.session.query(Project).filter(Project.project_name == project_name).one()
        project.project_active = True

        logger.info(f"Project[project_name = {project_name}] - activated")
        logger.debug("activate.execute() - Finish")
        return Command.SUCCESS


class ProjectActiveCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("active.execute() - Start")

        if "client" not in context:
            raise ContextKeyException("client")

        client = context["client"]
        project = context.session.query(Project).filter(Project.client_id == client.client_id,
                                                        Project.project_active == true()).first()

        if project:
            context["project"] = project
            found = True
        else:
            logger.warning("No active project found")
            found = False

        logger.debug("active.execute() - Finish")
        return found


class ProjectCreateCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("create.execute() - Start")

        if "project_name" not in context:
            raise ContextKeyException("client_name")

        if "client" not in context:
            raise ContextKeyException("client")

        project_name = context["project_name"]
        client = context["client"]

        project = Project(client_id=client.client_id, project_name=project_name)
        context.session.add(project)

        logger.info(f"Project[project_name = {project_name}] - created")
        logger.debug("create.execute() - Finish")
        return Command.SUCCESS


class ProjectReadCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("read.execute() - Start")

        if "project_name" not in context:
            raise ContextKeyException("project_name")

        if "client" not in context:
            raise ContextKeyException("client")

        project_name = context["project_name"]
        client = context["client"]

        project = context.session.query(Project).filter(Project.client_id == client.client_id,
                                                        Project.project_name == project_name).one()

        context["project"] = project

        logger.debug("read.execute() - Finish")
        return Command.SUCCESS


class ProjectUpdateCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("update.execute() - Start")

        if "project_name" not in context:
            raise ContextKeyException("project_name")

        if "client" not in context:
            raise ContextKeyException("client")

        updated = False
        project_name = context["project_name"]
        client = context["client"]

        project = context.session.query(Project).filter(Project.client_id == client.client_id,
                                                        Project.project_name == project_name).one()

        if "project_active" in context:
            project.project_active = context["project_active"]
            updated = True

        if "project_description" in context:
            project.project_description = context["project_description"]
            updated = True

        if "project_remark" in context:
            project.project_remark = context["project_remark"]
            updated = True

        if updated:
            logger.info(f"Project[project_name = {project_name}] - updated")
        else:
            logger.warning(f"Project[project_name = {project_name}] - not updated")

        logger.debug("update.execute() - Finish")
        return updated


class ProjectDeleteCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("delete.execute() - Start")

        if "project_name" not in context:
            raise ContextKeyException("project_name")

        if "client" not in context:
            raise ContextKeyException("client")

        project_name = context["project_name"]
        client = context["client"]

        project = context.session.query(Project).filter(Project.client_id == client.client_id,
                                                        Project.project_name == project_name).one()
        context.session.delete(project)

        logger.info(f"Project[project_name = {project_name}] - deleted")
        logger.debug("delete.execute() - Finish")
        return Command.SUCCESS


class ProjectListCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("list.execute() - Start")

        if "client" not in context:
            raise ContextKeyException("client")

        client = context["client"]

        projects = context.session.query(Project).filter(Project.client_id == client.client_id).order_by(
            Project.project_name).all()
        context["projects"] = projects

        logger.debug("list.execute() - Finish")
        return Command.SUCCESS


class ProjectExistCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("exist.execute() - Start")

        if "project_name" not in context:
            raise ContextKeyException("project_name")

        if "client" not in context:
            raise ContextKeyException("client")

        exist = True
        project_name = context["project_name"]
        client = context["client"]

        if context.session.query(Project).filter(Project.client_id == client.client_id,
                                                 Project.project_name == project_name).count() == 0:
            exist = False
            logger.warning(f"Project[project_name = {project_name}] - does not exist")

        logger.debug("exist.execute() - Finish")
        return exist


class ProjectNotExistCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("not_exist.execute() - Start")

        if "project_name" not in context:
            raise ContextKeyException("project_name")

        if "client" not in context:
            raise ContextKeyException("client")

        not_exist = True
        project_name = context["project_name"]
        client = context["client"]

        if context.session.query(Project).filter(Project.client_id == client.client_id,
                                                 Project.project_name == project_name).count() > 0:
            not_exist = False
            logger.warning(f"Project[project_name = {project_name}] - does exist")

        logger.debug("not_exist.execute() - Finish")
        return not_exist
