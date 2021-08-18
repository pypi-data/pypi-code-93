# -*- coding: utf-8 -*-
"""
    binalyzer_core.factory
    ~~~~~~~~~~~~~~~~~~~~~~

    This module implements factories used for cloning types.

    :copyright: 2021 Denis Vasilík
    :license: MIT
"""
from .properties import (
    PropertyBase,
    ValueProperty,
    ReferenceProperty,
    OffsetValueProperty,
    RelativeOffsetValueProperty,
    RelativeOffsetReferenceProperty,
    StretchSizeProperty,
    AutoSizeValueProperty,
)


class PropertyFactory(object):

    def __init__(self):
        self.property_factories = [
            OffsetValuePropertyFactory(),
            RelativeOffsetValuePropertyFactory(),
            RelativeOffsetReferencePropertyFactory(),
            StretchSizePropertyFactory(),
            AutoSizeValuePropertyFactory(),
            ReferencePropertyFactory(),
            ValuePropertyFactory(),
            PropertyBaseFactory(),
        ]

    def clone(self, prototype, template):
        factory = [f for f in self.property_factories
                   if f.is_clonable(prototype)][0]
        duplicate = factory.clone(prototype, template)
        return duplicate


class PropertyBaseFactory(object):

    def clone(self, prototype, template):
        property_base = PropertyBase(template)
        property_base.value_provider = type(
            prototype.value_provider)(property_base)
        return property_base

    def is_clonable(self, obj):
        return isinstance(obj, PropertyBase)


class ValuePropertyFactory(object):

    def clone(self, prototype, template):
        return ValueProperty(prototype.value, template)

    def is_clonable(self, obj):
        return isinstance(obj, ValueProperty)


class ReferencePropertyFactory(object):

    def clone(self, prototype, template):
        ref_property = ReferenceProperty(
            template,
            prototype.reference_name
        )
        ref_property.value_provider = type(
            prototype.value_provider)(ref_property)
        return ref_property

    def is_clonable(self, obj):
        return isinstance(obj, ReferenceProperty)


class OffsetValuePropertyFactory(object):

    def clone(self, prototype, template):
        return OffsetValueProperty(
            template,
            prototype.value,
        )

    def is_clonable(self, obj):
        return isinstance(obj, OffsetValueProperty)


class RelativeOffsetValuePropertyFactory(object):

    def clone(self, prototype, template):
        return RelativeOffsetValueProperty(
            template,
            prototype.ignore_boundary,
        )

    def is_clonable(self, obj):
        return isinstance(obj, RelativeOffsetValueProperty)


class RelativeOffsetReferencePropertyFactory(object):

    def clone(self, prototype, template):
        return RelativeOffsetReferenceProperty(
            template,
            prototype.reference_name,
        )

    def is_clonable(self, obj):
        return isinstance(obj, RelativeOffsetReferenceProperty)


class StretchSizePropertyFactory(object):

    def clone(self, prototype, template):
        return StretchSizeProperty(template)

    def is_clonable(self, obj):
        return isinstance(obj, StretchSizeProperty)


class AutoSizeValuePropertyFactory(object):

    def clone(self, prototype, template):
        return AutoSizeValueProperty(template)

    def is_clonable(self, obj):
        return isinstance(obj, AutoSizeValueProperty)


class TemplateFactory(object):

    def __init__(self):
        self.property_factory = PropertyFactory()

    def clone(self, prototype, id=None, parent=None):
        duplicate = type(prototype)()
        duplicate._prototype = prototype
        if id is None:
            duplicate.name = prototype.name
        else:
            duplicate.name = prototype.name + "-" + str(id)

        duplicate.parent = parent

        duplicate.offset_property = self.property_factory.clone(
            prototype.offset_property,
            duplicate
        )
        duplicate.size_property = self.property_factory.clone(
            prototype.size_property,
            duplicate
        )
        duplicate.boundary_property = self.property_factory.clone(
            prototype.boundary_property,
            duplicate
        )
        duplicate.padding_before_property = self.property_factory.clone(
            prototype.padding_before_property,
            duplicate
        )
        duplicate.padding_after_property = self.property_factory.clone(
            prototype.padding_after_property,
            duplicate
        )
        duplicate.count_property = self.property_factory.clone(
            prototype.count_property,
            duplicate
        )

        duplicate.signature = prototype.signature
        duplicate.hint = prototype.hint
        duplicate.text = prototype.text

        for child in prototype.children:
            self.clone(child, parent=duplicate)

        return duplicate
