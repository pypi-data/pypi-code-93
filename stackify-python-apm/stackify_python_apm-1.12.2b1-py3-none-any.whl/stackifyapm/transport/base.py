import logging
from copy import deepcopy

from stackifyapm.transport.timer import RepeatedTimer
from stackifyapm.conf.constants import AGENT_SEND_INTERVAL_IN_SEC
from stackifyapm.conf.constants import AGENT_TRACES_MAX_SIZE
from stackifyapm.protos import stackify_trace_pb2
from stackifyapm.utils.protobuf import to_protobuf

logger = logging.getLogger("stackifyapm.traces")


class BaseTransport(object):
    """
    Base Transport Class
    """
    def send_all(self):
        raise NotImplementedError

    def log_transaction(self, transaction):
        raise NotImplementedError


class ProtobufTransport(BaseTransport):
    """
    Protobuf Base Transport Class
    """
    _client = None
    traces = None

    def __init__(self):
        self.traces = stackify_trace_pb2.Traces()
        self.timer = RepeatedTimer(AGENT_SEND_INTERVAL_IN_SEC, self.send_all)
        self.timer.start()

    def send(self, traces):
        raise NotImplementedError

    def send_all(self):
        # send all traces in the queue
        if len(self.traces.traces):
            traces = deepcopy(self.traces)
            self.traces = stackify_trace_pb2.Traces()
            logger.debug("Sending {} transactions.".format(len(traces.traces)))
            self.send(traces)

    def _handle_trace(self, trace):
        # append trace to traces
        self.traces.traces.append(trace)

        # send traces if length is equal or more than the max size
        if len(self.traces.traces) >= AGENT_TRACES_MAX_SIZE:
            self.send_all()

    def log_transaction(self, transaction):
        config = self._client and self._client.config or None
        self._handle_trace(to_protobuf(transaction.to_dict(config=config)))
