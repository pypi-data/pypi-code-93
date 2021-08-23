from enum import Enum, IntEnum
import logging
import logging.config
import os

import click
from google.cloud.logging_v2.handlers._helpers import get_request_data
from google.cloud.logging_v2.client import Client
from google.cloud.logging_v2.logger import Logger
from google.cloud.logging_v2.resource import Resource

ENABLE_CLOUD_LOGGING = 'ENABLE_CLOUD_LOGGING'


class CloudLoggingSeverity(IntEnum):
    NOTSET = 0
    DEBUG = 100
    INFO = 200
    WARNING = 400
    ERROR = 500
    CRITICAL = 600


class Service(Enum):
    AppEngine = 'gae_app'
    Dataflow = 'dataflow_step'


class CloudLoggingHandler(logging.Handler):
    """Logs to Google Cloud Logging."""

    def __init__(self, level=logging.DEBUG, name='rbx', service=Service.AppEngine):
        super().__init__(level=level)
        if self.cloud_logging_enabled:
            if not isinstance(service, Service):
                service = Service(service)
            self.writer = CloudLoggingWriter(name=name, service=service)

    @property
    def cloud_logging_enabled(self):
        return all([
            bool(os.getenv(ENABLE_CLOUD_LOGGING, False)),
            bool(os.getenv('GOOGLE_CLOUD_PROJECT', False)),
        ])

    def emit(self, record):
        if self.cloud_logging_enabled:
            if record.exc_info:
                message = logging.Formatter().formatException(record.exc_info)
            else:
                message = self.format(record)

            inferred_http, _ = get_request_data()
            http_request = getattr(record, 'http_request', inferred_http or {})

            entry = {
                'message': message,
                'python_logger': record.name,
                **http_request,
            }

            self.writer.write_entry(entry, severity=CloudLoggingSeverity[record.levelname])


class CloudLoggingWriter:
    """The Writer is the object that calls the Cloud Logging API."""

    def __init__(self, name, service):
        project = os.getenv('GOOGLE_CLOUD_PROJECT')
        client = Client(project=project)

        self.log_name = f'projects/{project}/logs/{name}'
        self.logger = Logger(self.log_name, client)

        labels = {'project_id': project}
        if service is Service.AppEngine:
            labels.update({
                'module_id': os.getenv('GAE_SERVICE', 'N/A'),
                'version_id': os.getenv('GAE_VERSION', 'N/A')
            })

        self.resource = Resource(type=service.value, labels=labels)

    def write_entry(self, message, severity=CloudLoggingSeverity.NOTSET):
        self.logger.log_struct(
            message,
            log_name=self.log_name,
            resource=self.resource,
            severity=severity
        )


class ColourFormatter(logging.Formatter):

    def format(self, record):
        message = super().format(record)
        colours = {
            logging.INFO: {'bold': True},
            logging.WARNING: {'fg': 'yellow'},
            logging.ERROR: {'fg': 'bright_red'},
            logging.CRITICAL: {'fg': 'bright_white', 'bg': 'red'},
        }
        try:
            message = click.style(message, **colours[record.levelno])
        except KeyError:
            pass
        return message
