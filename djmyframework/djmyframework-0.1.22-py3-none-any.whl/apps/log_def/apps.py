from django.apps import AppConfig

from framework.translation import _


class LogDefConfig(AppConfig):
    """
    日志定义
    """
    name = 'log_def'
    verbose_name = _('日志定义')
