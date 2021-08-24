"""
apps.py
By IT小强xqitw.cn <mail@xqitw.cn>
At 1/24/21 11:11 AM
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoKeloveSettingConfig(AppConfig):
    """
    DjangoKeloveSettingConfig
    """

    label = 'django_kelove_setting'
    name = 'django_kelove_setting'
    verbose_name = _('Kelove Setting')

    kelove_settings = [
        'django_kelove_setting.kelove_settings.EmailSettings'
    ]
