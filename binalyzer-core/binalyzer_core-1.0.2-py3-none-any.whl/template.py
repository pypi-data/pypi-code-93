# -*- coding: utf-8 -*-
"""
    binalyzer_core.template
    ~~~~~~~~~~~~~~~~~~~~~~~

    This module implements the template.

    :copyright: 2021 Denis Vasilík
    :license: MIT
"""
from anytree import NodeMixin

from .binding import BackedBindingContext
from .properties import (
    ValueProperty,
    OffsetValueProperty,
    AutoSizeValueProperty,
    RelativeOffsetValueProperty,
)


class Template(NodeMixin, object):
    """This class implements the template mechanism as described in :ref:`template`.
    In addition, it inherits :class:`~anytree.node.nodemixin.NodeMixin` of the
    `anytree`_ library making it possible to create template trees.

    .. _anytree: https://anytree.readthedocs.io/en/latest/
    """

    def __init__(self, name=None, parent=None, children=None, binding_context=None, **kwargs):
        self._binding_context = binding_context
        if self._binding_context is None:
            self._binding_context = BackedBindingContext(self)
        self._prototype = None

        #: The name of the template
        self.name = name

        #: Children of the template
        if children:
            self.children = children

        self._count = ValueProperty(1)

        #: Parent of the template
        self.parent = parent

        #: :class:`~binalyzer.Offset` of the template
        self._offset = RelativeOffsetValueProperty(self)

        #: :class:`~binalyzer.Size` of the template
        self._size = AutoSizeValueProperty(self)

        #: :class:`~binalyzer.PaddingBefore` of the template
        self._padding_before = ValueProperty()

        #: :class:`~binalyzer.PaddingAfter` of the template
        self._padding_after = ValueProperty()

        #: :class:`~binalyzer.Boundary` of the template
        self._boundary = ValueProperty()

        self._signature = None
        self._hint = None
        self._text = None

    @property
    def offset(self):
        return self._offset.value

    @offset.setter
    def offset(self, value):
        self._offset = OffsetValueProperty(self, value)

    @property
    def offset_property(self):
        return self._offset

    @offset_property.setter
    def offset_property(self, value):
        self._offset = value
        self.clear_cache(self.root)

    @property
    def size(self):
        return self._size.value

    @size.setter
    def size(self, value):
        self._size = ValueProperty(value)
        self.clear_cache(self.root)

    @property
    def size_property(self):
        return self._size

    @size_property.setter
    def size_property(self, value):
        self._size = value
        self.clear_cache(self.root)

    @property
    def padding_before(self):
        return self._padding_before.value

    @padding_before.setter
    def padding_before(self, value):
        self._padding_before.value = value
        self.clear_cache(self.root)

    @property
    def padding_before_property(self):
        return self._padding_before

    @padding_before_property.setter
    def padding_before_property(self, value):
        self._padding_before = value
        self.clear_cache(self.root)

    @property
    def padding_after(self):
        return self._padding_after.value

    @padding_after.setter
    def padding_after(self, value):
        self._padding_after.value = value
        self.clear_cache(self.root)

    @property
    def padding_after_property(self):
        return self._padding_after

    @padding_after_property.setter
    def padding_after_property(self, value):
        self._padding_after = value
        self.clear_cache(self.root)

    @property
    def boundary(self):
        return self._boundary.value

    @boundary.setter
    def boundary(self, value):
        self._boundary.value = value
        self.clear_cache(self.root)

    @property
    def boundary_property(self):
        return self._boundary

    @boundary_property.setter
    def boundary_property(self, value):
        self._boundary = value
        self.clear_cache(self.root)

    @property
    def count(self):
        return self._count.value

    @count.setter
    def count(self, value):
        self._count.value = value

    @property
    def count_property(self):
        return self._count

    @count_property.setter
    def count_property(self, value):
        self._count = value
        self.clear_cache(self.root)

    @property
    def hint(self):
        return self._hint

    @hint.setter
    def hint(self, value):
        self._hint = value
        self.clear_cache(self.root)

    @property
    def hint_property(self):
        return self._hint

    @hint_property.setter
    def hint_property(self, value):
        self._hint = value
        self.clear_cache(self.root)

    @property
    def signature(self):
        return self._signature

    @signature.setter
    def signature(self, value):
        self._signature = value
        self.clear_cache(self.root)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        if value and isinstance(self.size_property, AutoSizeValueProperty):
            self.size_property = ValueProperty(len(value))
        self.clear_cache(self.root)

    @property
    def signature_property(self):
        return self._signature

    @signature_property.setter
    def signature_property(self, value):
        self._signature = value
        self.clear_cache(self.root)

    @property
    def text_property(self):
        return self._text

    @text_property.setter
    def text_property(self, value):
        self._text = value
        self.clear_cache(self.root)

    @property
    def absolute_address(self):
        """Provides the absolue address of the template within the binary stream.
        """
        if (isinstance(self.offset_property, ValueProperty)):
            return self.offset

        if (isinstance(self.offset_property, OffsetValueProperty) or
                isinstance(self.offset_property, RelativeOffsetValueProperty)):
            if self.parent:
                return self.offset + self.parent.absolute_address
            else:
                return self.offset

        raise TypeError()

    @property
    def value(self):
        """The :attr:`value` provides direct access to the data the template is
        bound to. It uses the :attr:`~binalyzer.BindingContext.data_provider`
        of the :class:`~binalyzer.BindingContext`.

        Reading from the property provides a binary stream of the area the
        template is bound to. Likewise, writing to the property writes a binary
        stream to the same area.
        """
        return self.binding_context.data_provider.read(self)

    @value.setter
    def value(self, value):
        self.size = len(value)
        self.binding_context.data_provider.write(self, value)

    @property
    def binding_context(self):
        """The :class:`~binalyzer.BindingContext` of the template
        """
        return self._binding_context

    @binding_context.setter
    def binding_context(self, value):
        self._binding_context = value
        self._binding_context.propagate(self)

    def _post_attach(self, parent):
        self._add_name_to_parent(parent)
        self.binding_context = parent.binding_context

    def _add_name_to_parent(self, parent):
        if self.name:
            parent.__dict__[self.name.replace("-", "_")] = self

    def clear_cache(self, template=None):
        if template is None:
            template = self
        template.offset_property.value_provider.clear_cache()
        template.size_property.value_provider.clear_cache()
        for child in template.children:
            self.clear_cache(child)
