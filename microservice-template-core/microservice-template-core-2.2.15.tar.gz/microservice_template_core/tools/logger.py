import logging
from microservice_template_core.settings import LoggerConfig, ServiceConfig
import logging_loki
from multiprocessing import Queue
from opentelemetry import trace

logger = None


class SpanFormatter(logging.Formatter):
    def format(self, record):
        trace_id = trace.get_current_span().get_span_context().trace_id
        if trace_id == 0:
            record.trace_id = None
        else:
            record.trace_id = "{trace:032x}".format(trace=trace_id)
        return super().format(record)


def get_logger():
    global logger
    if not logger:
        logger = logging.getLogger(ServiceConfig.SERVICE_NAME)
        logger.setLevel(LoggerConfig.LOG_LEVEL)

        loki_handler = logging_loki.LokiQueueHandler(
            Queue(-1),
            url=f"http://{LoggerConfig.LOKI_SERVER}:{LoggerConfig.LOKI_PORT}/loki/api/v1/push",
            tags={
                "service": ServiceConfig.SERVICE_NAME,
                "namespace": ServiceConfig.SERVICE_NAMESPACE,
                "pod": ServiceConfig.POD_NAME
            },
            version="1",
        )
        loki_handler.setFormatter(
            SpanFormatter(
                '%(levelname)s %(message)s trace_id=%(trace_id)s'
            )
        )

        console_handler = logging.StreamHandler()

        logger.addHandler(loki_handler)
        logger.addHandler(console_handler)

    return logger

