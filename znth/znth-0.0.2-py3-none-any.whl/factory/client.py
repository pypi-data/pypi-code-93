import logging

from znth.chain import Processor
from znth.command.client import ClientActivateCommand, ClientExistCommand, ClientNotExistCommand, ClientCreateCommand, \
    ClientReadCommand, ClientUpdateCommand, ClientDeleteCommand, ClientListCommand
from znth.factory.default import DefaultFactory


class ClientFactory(DefaultFactory):
    log_level = logging.INFO

    @classmethod
    def create_activate(cls, level = logging.ERROR) -> Processor:
        client = cls.create_default(level)
        client.validating.append(ClientExistCommand())
        client.processing.append(ClientActivateCommand())

        return client

    @classmethod
    def create_create(cls, level = logging.ERROR) -> Processor:
        client = cls.create_default(level)
        client.validating.append(ClientNotExistCommand())
        client.processing.append(ClientCreateCommand())

        return client

    @classmethod
    def create_read(cls, level = logging.ERROR) -> Processor:
        client = cls.create_default(level)
        client.validating.append(ClientExistCommand())
        client.processing.append(ClientReadCommand())

        return client

    @classmethod
    def create_update(cls, level = logging.ERROR) -> Processor:
        client = cls.create_default(level)
        client.validating.append(ClientExistCommand())
        client.processing.append(ClientUpdateCommand())

        return client

    @classmethod
    def create_delete(cls, level = logging.ERROR) -> Processor:
        client = cls.create_default(level)
        client.validating.append(ClientExistCommand())
        client.processing.append(ClientDeleteCommand())

        return client

    @classmethod
    def create_list(cls, level = logging.ERROR) -> Processor:
        client = cls.create_default(level)
        client.processing.append(ClientListCommand())

        return client
