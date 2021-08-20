import logging

from stackify.transport.agent.agent_socket import AgentSocket

from stackifyapm.conf.constants import AGENT_TRACES_PATH
from stackifyapm.transport.base import ProtobufTransport

logger = logging.getLogger("stackifyapm.traces")


class AgentSocketTransport(ProtobufTransport):
    """
    AgentSocketTransport class handles sending of data by group to StackifyAgent

    it will send data once the length of traces is more than or equal to AGENT_TRACES_MAX_SIZE
    it will also send data on every AGENT_SEND_INTERVAL_IN_SEC
    """
    _transport = AgentSocket()
    traces = None

    def __init__(self, client):
        self._client = client
        super(AgentSocketTransport, self).__init__()

    def send(self, traces):
        try:
            self._transport.send(
                self._client.config.socket_url + AGENT_TRACES_PATH,
                traces.SerializeToString(),
            )
            logger.debug("Success sending {} transactions.".format(len(traces.traces)))
        except Exception as e:
            logger.error("Failed sending {} transactions. Reason: {}.".format(len(traces.traces), e))
