import logging
from monitoring_template.settings import LoggerConfig, ServiceConfig
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
            url=f"{LoggerConfig.LOG_ENDPOINT}",
            tags={
                "service": ServiceConfig.SERVICE_NAME
            },
            version="1",
        )
        loki_handler.setFormatter(
            SpanFormatter(
                'time="%(asctime)s" service=%(name)s level=%(levelname)s %(message)s trace_id=%(trace_id)s'
            )
        )

        console_handler = logging.StreamHandler()

        logger.addHandler(loki_handler)
        logger.addHandler(console_handler)

    return logger

