from django.apps import AppConfig

from framework.translation import _


class SyncModelConfig(AppConfig):
    """同步django模型
    """
    name = 'sync_model'
    verbose_name = _('数据模型同步')
