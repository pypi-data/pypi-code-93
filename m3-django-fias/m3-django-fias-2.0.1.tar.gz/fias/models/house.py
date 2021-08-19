# coding: utf-8
from __future__ import unicode_literals, absolute_import

from fias.base_models import House as BaseHouse, Houseint, DelHouse as BaseDelHouse, DelHouseint

__all__ = ['House', 'HouseInt']


class House(BaseHouse):
    """
    Сведения по номерам домов улиц городов и населенных пунктов
    """
    class Meta:
        app_label = 'fias'
        verbose_name = 'Номер дома'
        verbose_name_plural = 'Номера домов'


class HouseInt(Houseint):
    """
    Интервалы домов
    """
    class Meta:
        app_label = 'fias'
        verbose_name = 'Интервал домов'
        verbose_name_plural = 'Интервалы домов'


class DelHouse(BaseDelHouse):
    """
    Удаленный номер дома
    """
    class Meta:
        app_label = 'fias'
        verbose_name = 'Удаленный номер дома'
        verbose_name_plural = 'Удаленные номера домов'


class DelHouseInt(DelHouseint):
    """
    Удаленный интервал домов
    """
    class Meta:
        app_label = 'fias'
        verbose_name = 'Удаленный интервал домов'
        verbose_name_plural = 'Удаленные интервалы домов'
