import logging

from sqlalchemy import true

from znth.chain import Command, ContextKeyException
from znth.command.database import DatabaseContext
from znth.models import Client


class ClientActivateCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("activate.execute() - Start")

        if "client_name" not in context:
            raise ContextKeyException("client_name")

        client_name = context["client_name"]

        for client in context.session.query(Client).filter(Client.client_active == true()).all():
            client.client_active = False

        client = context.session.query(Client).filter(Client.client_name == client_name).one()
        client.client_active = True

        logger.info(f"Client[client_name = {client_name}] - activated")
        logger.debug("activate.execute() - Finish")
        return Command.SUCCESS


class ClientActiveCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("active.execute() - Start")

        client = context.session.query(Client).filter(Client.client_active == true()).first()

        if client.client_active:
            context["client"] = client
            found = True
        else:
            logger.warning("No active client found")
            found = False

        logger.debug("active.execute() - Finish")
        return found


class ClientCreateCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("create.execute() - Start")

        if "client_name" not in context:
            raise ContextKeyException("client_name")

        client_name = context["client_name"]

        client = Client(client_name=client_name)
        context.session.add(client)

        logger.info(f"Client[client_name = {client_name}] - created")
        logger.debug("create.execute() - Finish")
        return Command.SUCCESS


class ClientReadCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("read.execute() - Start")

        if "client_name" not in context:
            raise ContextKeyException("client_name")

        client_name = context["client_name"]

        client = context.session.query(Client).filter(Client.client_name == client_name).one()

        context["client"] = client

        logger.debug("read.execute() - Finish")
        return Command.SUCCESS


class ClientUpdateCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("update.execute() - Start")

        if "client_name" not in context:
            raise ContextKeyException("client_name")

        updated = False
        client_name = context["client_name"]

        client = context.session.query(Client).filter(Client.client_name == client_name).one()

        if "client_active" in context:
            client.client_active = context["client_active"]
            updated = True

        if "client_description" in context:
            client.client_description = context["client_description"]
            updated = True

        if "client_remark" in context:
            client.client_remark = context["client_remark"]
            updated = True

        if updated:
            logger.info(f"Client[client_name = {client_name}] - updated")
        else:
            logger.warning(f"Client[client_name = {client_name}] - not updated")

        logger.debug("update.execute() - Finish")
        return updated


class ClientDeleteCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("delete.execute() - Start")

        if "client_name" not in context:
            raise ContextKeyException("client_name")

        client_name = context["client_name"]

        client = context.session.query(Client).filter(Client.client_name == client_name).one()
        context.session.delete(client)

        logger.info(f"Client[client_name = {client_name}] - deleted")
        logger.debug("delete.execute() - Finish")
        return Command.SUCCESS


class ClientListCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("list.execute() - Start")

        clients = context.session.query(Client).order_by(Client.client_name).all()
        context["clients"] = clients

        logger.debug("list.execute() - Finish")
        return Command.SUCCESS


class ClientExistCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("exist.execute() - Start")

        if "client_name" not in context:
            raise ContextKeyException("client_name")

        exists = True
        client_name = context["client_name"]

        if context.session.query(Client).filter(Client.client_name == client_name).count() == 0:
            exists = False
            logger.warning(f"Client[client_name = {client_name}] - does not exist")

        logger.debug("exist.execute() - Finish")
        return exists


class ClientNotExistCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("not_exist.execute() - Start")

        if "client_name" not in context:
            raise ContextKeyException("client_name")

        not_exist = True
        client_name = context["client_name"]

        if context.session.query(Client).filter(Client.client_name == client_name).count() > 0:
            not_exist = False
            logger.warning(f"Client[client_name = {client_name}] - does exist")

        logger.debug("not_exist.execute() - Finish")
        return not_exist
