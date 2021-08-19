#coding: utf-8
from __future__ import unicode_literals, absolute_import

from django.utils.encoding import python_2_unicode_compatible

__all__ = [
    'ActStat', 'CenterSt', 'CurentSt',
    'EstStat', 'HSTStat', 'IntvStat',
    'OperStat', 'StrStat'
]

from fias.base_models import Actstat, Centerst, Curentst, \
    Eststat, Hststat, Intvstat, Operstat, Strstat


@python_2_unicode_compatible
class ActStat(Actstat):
    """
    Статус актуальности ФИАС
    """
    class Meta:
        app_label = 'fias'
        verbose_name = 'Статус актуальности ФИАС'
        verbose_name_plural = 'Статусы актуальности ФИАС'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class CenterSt(Centerst):
    """
    Статус центра
    """
    class Meta:
        app_label = 'fias'
        verbose_name = 'Статус центра'
        verbose_name_plural = 'Статусы центров'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class CurentSt(Curentst):
    """
    Статус актуальности КЛАДР 4.0
    """
    class Meta:
        app_label = 'fias'
        verbose_name = 'Статус актуальности КЛАДР 4.0'
        verbose_name_plural = 'Статусы актуальности КЛАДР 4.0'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class EstStat(Eststat):
    """
    Признак владения
    """
    class Meta:
        app_label = 'fias'
        verbose_name = 'Признак владения'
        verbose_name_plural = 'Признаки владения'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class HSTStat(Hststat):
    """
    Статус состояния домов
    """
    class Meta:
        app_label = 'fias'
        verbose_name = 'Статус состояния домов'
        verbose_name_plural = 'Статусы состояния домов'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class IntvStat(Intvstat):
    """
    Статус интервалов домов
    """
    class Meta:
        app_label = 'fias'
        verbose_name = 'Статус интервала домов'
        verbose_name_plural = 'Статусы интервалов домов'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class OperStat(Operstat):
    """
    Статус действия
    """
    class Meta:
        app_label = 'fias'
        verbose_name = 'Статус действия'
        verbose_name_plural = 'Статусы действия'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class StrStat(Strstat):
    """
    Признак строения
    """
    class Meta:
        app_label = 'fias'
        verbose_name = 'Признак строения'
        verbose_name_plural = 'Признаки строения'

    def __str__(self):
        return self.name
