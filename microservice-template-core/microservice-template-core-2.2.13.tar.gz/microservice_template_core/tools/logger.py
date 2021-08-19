import logging
from microservice_template_core.settings import LoggerConfig, ServiceConfig
import logging_loki
from multiprocessing import Queue

logger = None


def get_logger():
    global logger
    if not logger:
        logger = logging.getLogger(ServiceConfig.SERVICE_NAME)
        logger.setLevel(LoggerConfig.LOG_LEVEL)
        log_format = logging.Formatter('[%(levelname)s] - %(message)s')

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
        loki_handler.setFormatter(log_format)

        console_handler = logging.StreamHandler()

        logger.addHandler(loki_handler)
        logger.addHandler(console_handler)

    return logger

