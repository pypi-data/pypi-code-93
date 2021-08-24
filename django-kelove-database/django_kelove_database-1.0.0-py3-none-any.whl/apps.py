"""
apps.py
By IT小强xqitw.cn <mail@xqitw.cn>
At 2/1/21 2:05 PM
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoKeloveDatabaseConfig(AppConfig):
    """
    DjangoKeloveDatabaseConfig
    """

    label = 'django_kelove_database'
    name = 'django_kelove_database'
    verbose_name = _('Kelove Database')

    kelove_settings = [
        'django_kelove_database.kelove_settings.JSONFieldSettings',
        'django_kelove_database.kelove_settings.CkfinderFieldSettings',
        'django_kelove_database.kelove_settings.EditorMdFieldSettings',
        'django_kelove_database.kelove_settings.EditorCkFieldSettings',
    ]
