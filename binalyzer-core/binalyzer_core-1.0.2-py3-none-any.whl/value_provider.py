# -*- coding: utf-8 -*-
"""
    binalyzer_core.value_provider
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements value providers.

    :copyright: 2021 Denis Vasilík
    :license: MIT
"""
from .template_engine import TemplateEngine


def value_cache(func):
    def wrapper(*args, **kwargs):
        if args[0]._cached_value is None:
            args[0]._cached_value = func(*args, **kwargs)
        return args[0]._cached_value
    return wrapper


class ValueProviderBase(object):

    def __init__(self, property):
        self.property = property
        self._cached_value = None

    def get_value(self):
        pass

    def set_value(self, value):
        pass

    def clear_cache(self):
        self._cached_value = None


class ValueProvider(ValueProviderBase):

    def __init__(self, property):
        self._value = 0
        super(ValueProvider, self).__init__(property)

    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = value


class TemplateValueProvider(ValueProviderBase):

    def __init__(self, property):
        self.byteorder = 'little'
        super(TemplateValueProvider, self).__init__(property)

    @value_cache
    def get_value(self):
        return int.from_bytes(
            self.property.template.value,
            self.byteorder,
        )

    def set_value(self, value):
        raise RuntimeError(
            'Read-Only: Unable to assign a value to template using a value '
            'provider.'
        )


class OffsetValueProvider(ValueProvider):

    def __init__(self, property):
        self._engine = TemplateEngine()
        super(OffsetValueProvider, self).__init__(property)

    @value_cache
    def get_value(self):
        absolute_address = 0
        template = self.property.template
        if template.parent:
            absolute_address += template.parent.absolute_address
        absolute_address += self._value
        absolute_address += self._engine._get_boundary_offset(
            absolute_address, template.boundary
        )
        if template.parent:
            relative_offset = absolute_address - template.parent.absolute_address
        else:
            relative_offset = absolute_address
        return relative_offset

    def set_value(self, value):
        self._value = value


class RelativeOffsetValueProvider(ValueProviderBase):

    def __init__(self, property):
        self.ignore_boundary = False
        self._engine = TemplateEngine()
        super(RelativeOffsetValueProvider, self).__init__(property)

    @value_cache
    def get_value(self):
        return self._engine.get_offset(self.property.template,
                                       self.ignore_boundary)

    def set_value(self, value):
        raise RuntimeError(
            'Read-Only: Assigning a value to a relative offset is not allowed.'
        )


class RelativeOffsetReferenceValueProvider(ValueProviderBase):

    def __init__(self, property):
        self._engine = TemplateEngine()
        super(RelativeOffsetReferenceValueProvider, self).__init__(property)

    @value_cache
    def get_value(self):
        return (self._engine.get_offset(self.property.template) +
                self.property.template.value)

    def set_value(self, value):
        self.clear_cache()
        self.property.template.value = value


class AutoSizeValueProvider(ValueProviderBase):

    def __init__(self, property):
        self._engine = TemplateEngine()
        super(AutoSizeValueProvider, self).__init__(property)

    @value_cache
    def get_value(self):
        return self._engine.get_size(self.property.template)

    def set_value(self, value):
        raise RuntimeError('Not supported')


class StretchSizeValueProvider(ValueProvider):

    def __init__(self, property):
        self._engine = TemplateEngine()
        super(StretchSizeValueProvider, self).__init__(property)

    @value_cache
    def get_value(self):
        return self._engine.get_max_size(self.property.template)

    def set_value(self, value):
        raise RuntimeError('Not supported')
