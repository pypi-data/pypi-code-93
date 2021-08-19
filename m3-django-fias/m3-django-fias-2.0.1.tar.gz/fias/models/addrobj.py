# coding: utf-8
from __future__ import unicode_literals, absolute_import

import six
from django.utils.encoding import python_2_unicode_compatible

from fias.base_models import Addrobj, DelAddrobj

__all__ = ['AddrObj']


@python_2_unicode_compatible
class AddrObj(Addrobj):
    """
    Классификатор адресообразующих элементов
    """
    class Meta:
        app_label = 'fias'
        verbose_name = 'Адресообразующий элемент'
        verbose_name_plural = 'Адресообразующие элементы'
        index_together = (
            ('aolevel', 'shortname'),
            ('shortname', 'formalname'),
            ('aolevel', 'formalname'),
        )
        ordering = ['aolevel', 'formalname']

    def full_name(self, depth=None, formal=False):
        assert isinstance(depth, six.integer_types), 'Depth must be integer'

        if not self.parentguid or self.aolevel <= 1 or depth <= 0:
            if formal:
                return self.get_formal_name()
            return self.get_natural_name()
        else:
            parent = AddrObj.objects.get(pk=self.parentguid)
            return '{0}, {1}'.format(parent.full_name(depth-1, formal), self)

    def get_natural_name(self):
        if self.aolevel == 1:
            return '{0} {1}'.format(self.formalname, self.shortname)
        return self.get_formal_name()

    def get_formal_name(self):
        return '{0} {1}'.format(self.shortname, self.formalname)

    def __str__(self):
        return self.get_natural_name()

    def full_address(self):
        return self.full_name(5)


class DelAddrObj(DelAddrobj):
    """
    Удаленный элемент классификатора адресообразующих элементов
    """
    class Meta:
        app_label = 'fias'
        verbose_name = 'Удаленный адресообразующий элемент'
        verbose_name_plural = 'Удаленные адресообразующие элементы'