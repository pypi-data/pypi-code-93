import logging

from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules

from framework.translation import _


class MyadminConfig(AppConfig):
    #app_label = 'myadmin'
    name = 'myadmin'
    verbose_name = _('MyAdmin 管理系统')

    def ready(self):
        logging.info('myadmin ready')
        logging.info('register user resource')
        autodiscover_modules('admin_resource')
