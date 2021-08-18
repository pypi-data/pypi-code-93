# -*- coding: utf-8 -*-
"""
    binalyzer_core.properties
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements template properties.

    :copyright: 2021 Denis Vasilík
    :license: MIT
"""
from anytree import findall_by_attr

from .value_provider import (
    ValueProvider,
    TemplateValueProvider,
    AutoSizeValueProvider,
    OffsetValueProvider,
    RelativeOffsetValueProvider,
    StretchSizeValueProvider,
)


class PropertyBase(object):

    def __init__(self, template=None, value_provider=None):
        self._template = template
        self._value_provider = value_provider

    @property
    def template(self):
        return self.get_template()

    @template.setter
    def template(self, value):
        self.set_template(value)

    @property
    def value(self):
        return self.get_value()

    @value.setter
    def value(self, value):
        self.set_value(value)

    @property
    def value_provider(self):
        return self.get_value_provider()

    @value_provider.setter
    def value_provider(self, value):
        self.set_value_provider(value)

    def get_value(self):
        return self.value_provider.get_value()

    def set_value(self, value):
        self.value_provider.set_value(value)

    def get_template(self):
        return self._template

    def set_template(self, value):
        self._template = value

    def get_value_provider(self):
        return self._value_provider

    def set_value_provider(self, value):
        self._value_provider = value


class ValueProperty(PropertyBase):

    def __init__(self, value=0, template=None):
        super(ValueProperty, self).__init__(template, ValueProvider(self))
        self.value = value


class ReferenceProperty(PropertyBase):

    def __init__(self, template, reference_name, value_provider=None):
        self.origin = template
        self.reference_name = reference_name
        if value_provider is None:
            value_provider = TemplateValueProvider(self)
        super(ReferenceProperty, self).__init__(None, value_provider)

    def get_template(self):
        return self._find(self.origin, self.reference_name)

    def set_template(self, value):
        raise RuntimeError(
            'Unable to assign template to reference property.'
        )

    def _find(self, template, reference_name):
        while template.parent:
            result = findall_by_attr(template.parent, reference_name)
            if result:
                return result[0]
            template = template.parent
        raise RuntimeError(
            'Unable to find referenced template "' + reference_name + '".'
        )


class OffsetValueProperty(PropertyBase):

    def __init__(self, template, value):
        super(OffsetValueProperty, self).__init__(
            template, OffsetValueProvider(self))
        self.value = value


class RelativeOffsetValueProperty(PropertyBase):

    def __init__(self, template, ignore_boundary=False):
        self.ignore_boundary = ignore_boundary
        super(RelativeOffsetValueProperty, self).__init__(
            template, RelativeOffsetValueProvider(self))


class RelativeOffsetReferenceProperty(ReferenceProperty):

    def __init__(self, template, reference_name):
        super(RelativeOffsetReferenceProperty, self).__init__(
            template, reference_name, RelativeOffsetValueProvider(self))


class StretchSizeProperty(PropertyBase):

    def __init__(self, template):
        super(StretchSizeProperty, self).__init__(
            template, StretchSizeValueProvider(self))


class AutoSizeValueProperty(PropertyBase):

    def __init__(self, template):
        super(AutoSizeValueProperty, self).__init__(
            template, AutoSizeValueProvider(self))
