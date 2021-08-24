import logging
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__)))

import eventy.config
import eventy.config.django
from eventy.logging import GkeHandler, SimpleHandler
from app import settings

# Configure Eventy
eventy.config.SERVICE_NAME = 'eventy-django-test'
# Django integration
eventy.config.django.DJANGO_ACCESS_HEALTH_ROUTE = '/health'
eventy.config.django.DJANGO_ACCESS_DISABLE_HEALTH_LOGGING = settings.SKIP_HEALTHCHECK_LOGGING

# Setup logging
root_logger = logging.getLogger()
root_logger.setLevel(settings.LOG_LEVEL)

root_handler: logging.Handler

if settings.GKE_LOGGING:
    root_handler = GkeHandler()
else:
    root_handler = SimpleHandler(colored=settings.COLORED_LOGGING)

root_logger.addHandler(root_handler)
# logging.getLogger('django.server').addHandler(root_handler)

