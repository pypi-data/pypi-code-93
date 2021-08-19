# coding: utf-8
from __future__ import unicode_literals, absolute_import
from django.utils.encoding import python_2_unicode_compatible

from django.db import models

__all__ = ['SocrBase']

from fias.base_models import Socrbase


@python_2_unicode_compatible
class SocrBase(Socrbase):
    """
    Тип адресного объекта
    """
    class Meta:
        app_label = 'fias'
        verbose_name = 'Тип адресного объекта'
        verbose_name_plural = 'Типы адресных объектов'
        index_together = (
            ('level', 'scname'),
        )
        ordering = ['level', 'scname']

    item_weight = models.PositiveSmallIntegerField('Вес типа объекта', default=64,
                                                   help_text='Используется для сортировки результатов поиска'
                                                             ' с помощью Sphinx. Допустимые значения 1-128.'
                                                             ' Чем больше число, тем выше объекты данного'
                                                             ' типа в поиске.')

    def __str__(self):
        return self.socrname
