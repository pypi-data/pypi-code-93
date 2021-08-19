# coding: utf-8
from __future__ import unicode_literals, absolute_import

from fias.base_models import Landmark, DelLandmark

__all__ = ['LandMark']


class LandMark(Landmark):
    """
    Описание мест расположения имущественных объектов
    """
    class Meta:
        app_label = 'fias'
        verbose_name = 'Место расположения имущественного объекта'
        verbose_name_plural = 'Места расположения имущественных объектов'


class DelLandMark(DelLandmark):
    """
    Удаленное место расположение имущественного объекта
    """
    class Meta:
        app_label = 'fias'
        verbose_name = 'Удаленный элемент РИО'
        verbose_name_plural = 'Удаленные элементы РИО'
