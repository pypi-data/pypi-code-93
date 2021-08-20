import logging

from znth.chain import Processor
from znth.command.database import DatabaseCreateCommand
from znth.factory.default import DefaultFactory


class InitFactory(DefaultFactory):
    log_level = logging.INFO

    @classmethod
    def create_init(cls, level = logging.ERROR) -> Processor:
        client = cls.create_default(level)
        client.processing.append(DatabaseCreateCommand())

        return client
