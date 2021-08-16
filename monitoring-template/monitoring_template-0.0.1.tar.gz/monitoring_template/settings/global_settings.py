import os


class ServiceConfig:
    SERVICE_NAME = os.getenv('SERVICE_NAME', 'microservice_template_core')
    configuration = {}


class LoggerConfig:
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
    LOGGING_VERBOSE = os.getenv('LOGGING_VERBOSE', False)
    LOKI_SERVER = os.getenv('LOKI_SERVER', '127.0.0.1')
    LOKI_PORT = os.getenv('LOKI_PORT', 3100)


class TracerConfig:
    JAEGER_SERVER = os.getenv('JAEGER_SERVER', '127.0.0.1')
    JAEGER_PORT = int(os.getenv('JAEGER_PORT', 6831))
