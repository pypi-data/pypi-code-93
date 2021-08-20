import os


class ServiceConfig:
    SERVICE_NAME = os.getenv('SERVICE_NAME', 'monitoring_template')


class LoggerConfig:
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
    LOGGING_VERBOSE = os.getenv('LOGGING_VERBOSE', False)
    LOG_ENDPOINT = os.getenv('LOG_ENDPOINT', 'https://some_server:8081/v1/push')


class TracerConfig:
    AGENT_HOSTNAME = os.getenv('AGENT_HOSTNAME', '127.0.0.1')
    AGENT_PORT = int(os.getenv('AGENT_PORT', 6831))
