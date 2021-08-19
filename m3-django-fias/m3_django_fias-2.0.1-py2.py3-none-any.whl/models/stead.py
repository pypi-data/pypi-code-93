#coding: utf-8
from __future__ import unicode_literals, absolute_import

from django.utils.encoding import python_2_unicode_compatible

from fias.base_models import Stead as BaseStead

__all__ = ['Stead']


@python_2_unicode_compatible
class Stead(BaseStead):
    """
    Сведения о земельных участках
    """
    class Meta:
        app_label = 'fias'
        verbose_name = 'Земельный участок'
        verbose_name_plural = 'Земельные участки'

    def __str__(self):
        return self.number
