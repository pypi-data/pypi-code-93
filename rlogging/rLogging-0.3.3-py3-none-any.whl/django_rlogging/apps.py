import rlogging
import rlogging.config
from django.apps.config import AppConfig
from django.conf import settings


class RLoggingAppConfig(AppConfig):
    """ Конфигурация django приложения для подключения к django """

    name = 'django_rlogging'
    verbose_name = 'rlogging for django'

    def ready(self):
        if getattr(settings, 'RLOGGING_NOT_USE', False):
            rlogging.config.RLOGGING_LOGGER = 'rlogging.entities.base.loggers.DevNullLogger'

        setupCallback = getattr(settings, 'RLOGGING_SETUP', None)

        if setupCallback is not None:
            setupCallback()

        rlogging.start_loggers()
