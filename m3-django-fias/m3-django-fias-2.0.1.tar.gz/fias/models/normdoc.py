# coding: utf-8
from __future__ import unicode_literals, absolute_import

from django.utils.encoding import python_2_unicode_compatible

from fias.base_models import Ndoctype, Normdoc, DelNormdoc

__all__ = ['NormDoc', 'NDocType']


@python_2_unicode_compatible
class NDocType(Ndoctype):
    """
    Тип нормативного документа
    """
    class Meta:
        app_label = 'fias'
        verbose_name = 'Тип нормативного документа'
        verbose_name_plural = 'Типы нормативных документов'

    def __str__(self):
        return self.name


class NormDoc(Normdoc):
    """
    Сведения по нормативному документу,
    являющемуся основанием присвоения адресному элементу наименования
    """
    class Meta:
        app_label = 'fias'
        verbose_name = 'Нормативный документ'
        verbose_name_plural = 'Нормативные документы'


class DelNormDoc(DelNormdoc):
    """
    Удаленный нормативный документ
    """
    class Meta:
        app_label = 'fias'
        verbose_name = 'Удаленный нормативный документ'
        verbose_name_plural = 'Удаленные нормативные документы'