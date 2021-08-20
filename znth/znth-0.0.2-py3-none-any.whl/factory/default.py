import logging

from znth.chain import Processor
from znth.command.common import ReportCommand, ZenithCommand, ZenithDirectoryCommand, LoggingCommand, \
    AuthenticationCommand, ReadlineCommand
from znth.command.database import DatabaseSetupCommand, DatabaseSessionCommand, DatabaseCreateCommand
from znth.command.node import NodeUUIDCommand


class DefaultFactory(object):
    log_level = logging.INFO

    @classmethod
    def create_default(cls, level) -> Processor:
        default = Processor()

        default.reporting.append(ReportCommand())

        default.initialization.append(ZenithCommand())
        default.initialization.append(ZenithDirectoryCommand())
        default.initialization.append(LoggingCommand(level))
        default.initialization.append(DatabaseSetupCommand())
        default.initialization.append(DatabaseSessionCommand())
        default.initialization.append(NodeUUIDCommand())
        default.initialization.append(ReadlineCommand())

        default.authentication.append(AuthenticationCommand())

        return default
