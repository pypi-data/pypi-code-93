import logging

from stackifyapm.conf import constants
from stackifyapm.transport.agent import AgentSocketTransport
from stackifyapm.transport.default import DefaultTransport
from stackifyapm.transport.http import AgentHTTPTransport
from stackifyapm.transport.logger import LoggingTransport

logger = logging.getLogger("stackifyapm.traces")


class TransportTypes(object):
    """
    Transport Type class that will determine which transport to use depending on users config.

    Types:
    * DEFAULT - Logging transport that will log transaction data into a log file
    * AGENT_SOCKET - HTTP warapped Unix Socket Domain that will send logs to the StackifyAgent
    * AGENT_HTTP - Transport that will send logs to the StackifyAgent using HTTP request
    """
    AGENT_HTTP = constants.TRANSPORT_AGENT_HTTP
    AGENT_SOCKET = constants.TRANSPORT_AGENT_SOCKET
    DEFAULT = constants.TRANSPORT_DEFAULT
    LOGGING = constants.TRANSPORT_LOGGING

    @classmethod
    def get_transport(self, client):
        # return which transport to use
        if client.config.transport == TransportTypes.AGENT_SOCKET:
            logger.debug('Setting up AGENT SOCKET TRANSPORT.')
            return AgentSocketTransport(client=client)
        if client.config.transport == TransportTypes.AGENT_HTTP:
            logger.debug('Setting up AGENT HTTP TRANSPORT.')
            return AgentHTTPTransport(client=client)
        if client.config.transport == TransportTypes.LOGGING:
            logger.debug('Setting up SERVERLESS LOGGING TRANSPORT.')
            return LoggingTransport(client=client)

        # setup stackify apm logging
        logger.debug('Setting up STACKIFYAPM LOGGING TRANSPORT.')
        return DefaultTransport(client=client)


class Transport(object):
    """
    Transport class an abstract class for different transport types
    """
    def __init__(self, client):
        self._client = client
        self.transport = TransportTypes.get_transport(client=self._client)

    def handle_transaction(self, transaction):
        # abstract method for handling transactions
        # called when a transaction is done (request finished)
        logger.debug('Handling transaction with id: {}.'.format(transaction.get_id()))
        try:
            self.transport.log_transaction(transaction)
        except Exception as e:
            logger.error('Having problem logging transaction. Error: {}'.format(e))

    def send_all(self):
        # handles all remaining transactions
        self.transport.send_all()
