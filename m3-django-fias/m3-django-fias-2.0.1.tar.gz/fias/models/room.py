#coding: utf-8
from __future__ import unicode_literals, absolute_import

from django.utils.encoding import python_2_unicode_compatible

from fias.base_models import Flattype, Roomtype, Room as BaseRoom

__all__ = ['Room', 'FlatType', 'RoomType']


class FlatType(Flattype):
    """
    Классификатор типов помещения или офиса
    """
    class Meta:
        app_label = 'fias'
        verbose_name = 'Тип помещения или офиса'
        verbose_name_plural = 'Типы помещения или офиса'


class RoomType(Roomtype):
    """
    Классификатор типов комнат
    """
    class Meta:
        app_label = 'fias'
        verbose_name = 'Тип комнаты'
        verbose_name_plural = 'Типы комнат'


@python_2_unicode_compatible
class Room(BaseRoom):
    """
    Классификатор помещений
    """
    class Meta:
        app_label = 'fias'
        verbose_name = 'Помещение'
        verbose_name_plural = 'Помещения'

    def __str__(self):
        return self.flatnumber
