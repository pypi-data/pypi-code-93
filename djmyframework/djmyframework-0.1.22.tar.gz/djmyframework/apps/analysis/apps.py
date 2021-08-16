from django.apps import AppConfig

from framework.translation import _


class AnalysisConfig(AppConfig):
    """
    查询系统
    """
    name = 'analysis'
    verbose_name = _('查询分析系统')
