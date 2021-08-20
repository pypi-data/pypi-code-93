import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from znth.chain import Command, CommandState, Context, ContextKeyException
from znth.models import Base


class DatabaseContext(Context):
    engine = None
    db_filename: str = None
    session = None


class DatabaseSetupCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("setup.execute() - Start")

        if "db_filename" not in context:
            raise ContextKeyException("db_filename")

        context["db_engine"] = create_engine(f"sqlite:///{context['db_filename']}")

        logger.debug("setup.execute() - Finish")
        return Command.SUCCESS


class DatabaseCreateCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("create.execute() - Start")

        if "db_filename" not in context:
            raise ContextKeyException("db_filename")

        if "db_engine" not in context:
            raise ContextKeyException("db_engine")

        Base.metadata.create_all(context["db_engine"])
        logger.info(f"Created db: {context['db_filename']}")

        logger.debug("create.execute() - Finish")
        return Command.SUCCESS


class DatabaseDropCommand(Command):
    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("create.execute() - Start")

        if "db_filename" not in context:
            raise ContextKeyException("db_filename")

        if "db_engine" not in context:
            raise ContextKeyException("db_engine")

        Base.metadata.drop_all(context["db_engine"])
        logger.info(f"Dropped db: {context['db_filename']}")

        logger.debug("create.execute() - Finish")
        return Command.SUCCESS


class DatabaseSessionCommand(Command):
    def __init__(self):
        self.has_session = False
        self.session = None

    def execute(self, context: DatabaseContext) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("session.execute() - Start")

        if "db_engine" not in context:
            raise ContextKeyException("db_engine")

        engine = context["db_engine"]
        Session = sessionmaker(bind=engine)
        self.session = Session()
        context.session = self.session
        self.has_session = True

        logger.debug("session.execute() - Finish")
        return Command.SUCCESS

    def post_execute(self, context: Context, state: CommandState, error: Exception = None) -> None:
        logger = logging.getLogger(__name__)
        logger.debug("session.post_execute() - Start")

        if state == CommandState.SUCCESS:
            self.session.commit()
            logger.debug("session.commit()")
        else:
            if self.has_session:
                self.session.rollback()
                logger.debug("session.rollback()")

        logger.debug("session.post_execute() - Finish")
