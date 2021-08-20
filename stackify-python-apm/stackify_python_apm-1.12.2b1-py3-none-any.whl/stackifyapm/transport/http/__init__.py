import logging
import requests
import retrying

from stackifyapm.conf.constants import AGENT_TRACES_PATH
from stackifyapm.transport.base import ProtobufTransport

logger = logging.getLogger("stackifyapm.traces")


class AgentHTTPTransport(ProtobufTransport):
    """
    AgentHTTPTransport class handles sending of data by group to StackifyAgent using http request

    it will send data once the length of traces is more than or equal to AGENT_TRACES_MAX_SIZE
    it will also send data on every AGENT_SEND_INTERVAL_IN_SEC
    """
    traces = None

    def __init__(self, client):
        self._client = client
        self._session = requests.Session()

        super(AgentHTTPTransport, self).__init__()

    @retrying.retry(wait_exponential_multiplier=1000, stop_max_delay=32000)
    def _post(self, url, payload):
        headers = {
            'Content-Type': 'application/x-protobuf',
        }
        try:
            return self._session.post(url, payload, headers=headers, verify=False)
        except Exception as e:
            logger.debug('HTTP transport exception: {}.'.format(e))
            raise

    def send(self, traces):
        try:
            response = self._post(
                self._client.config.http_endpoint + AGENT_TRACES_PATH,
                traces.SerializeToString(),
            )
            logger.debug("Success sending {} transactions. Status: {}.".format(len(traces.traces), response.status_code))
        except Exception as e:
            logger.error("Failed sending {} transactions. Reason: {}.".format(len(traces.traces), e))
