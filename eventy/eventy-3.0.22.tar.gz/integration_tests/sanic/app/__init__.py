import logging

from app import settings

import eventy.config
import eventy.config.sanic
from eventy.logging import GkeHandler, SimpleHandler

# Configure Eventy
eventy.config.SERVICE_NAME = 'test-sanic-integration'
eventy.config.sanic.SANIC_ACCESS_HEALTH_ROUTE = '/health'
eventy.config.sanic.SANIC_ACCESS_DISABLE_HEALTH_LOGGING = settings.SKIP_HEALTHCHECK_LOGGING

# Setup logging
root_logger = logging.getLogger()
root_logger.setLevel(settings.LOG_LEVEL)

root_handler: logging.Handler

if settings.GKE_LOGGING:
    root_handler = GkeHandler()
else:
    root_handler = SimpleHandler(colored=settings.COLORED_LOGGING)

root_logger.addHandler(root_handler)
