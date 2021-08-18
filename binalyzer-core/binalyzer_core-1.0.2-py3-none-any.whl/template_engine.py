# -*- coding: utf-8 -*-
"""
    binalyzer_core.template_engine
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements the mechanics of the template concept.

    :copyright: 2021 Denis Vasilík
    :license: MIT
"""
from anytree.util import rightsibling

from .utils import rightsiblings


class TemplateEngine(object):
    """
    """

    def get_offset(self, template, ignore_boundary=False):
        """Returns the offset relative to a parent or predecessor taking a given
        boundary into account. It is possible to ignore the boundary by setting
        `ìgnore_boundary` to `True`.
        """
        offset = template.padding_before

        if not ignore_boundary:
            offset += self._get_boundary_offset_relative_to_parent(template)

        offset += self._get_offset_at_end_of_predecessor(template)

        if not ignore_boundary:
            offset += self._get_boundary_offset_at_end_of_predecessor(template)

        return offset

    def get_size(self, template):
        """Returns the actual size of the given template taking a given boundary
        into account.
        """
        size = self.get_size_of_children(template.children)
        size = self._get_multiple_of_boundary(size, template.boundary)
        return size

    def get_size_of_siblings(self, siblings):
        # Siblings represent only a part of a template's children. Thus, their
        # size is determined using padding before, padding after, and their size.
        return sum(self.get_size_of_sibling(sibling) for sibling in siblings)

    def get_size_of_sibling(self, sibling):
        return (sibling.padding_before +
                sibling.size +
                sibling.padding_after)

    def get_size_of_children(self, children):
        # Calculates the size used by the children taking the offset into
        # account. Summing up the sizes of the children is not accurate enough,
        # because one of the children could be placed specifically using an
        # offset.
        if not children:
            return 0
        # Assumption: Maximum always reached at last children
        last_children = children[-1]
        # NOTE: Offset already contains the value of padding before.
        size = (last_children.offset +
                last_children.size +
                last_children.padding_after)
        return size

    def get_max_size(self, template):
        """Returns a template's maximum possible size depending on the offset of
        its successor or size of it's parent.
        """
        from .properties import AutoSizeValueProperty, OffsetValueProperty

        next_sibling = rightsibling(template)
        if next_sibling and isinstance(next_sibling.offset_property,
                                       OffsetValueProperty):
            return next_sibling.offset - template.offset
        elif (next_sibling and template.parent and
              not isinstance(template.parent.size_property, AutoSizeValueProperty)):
            siblings = rightsiblings(template)
            return template.parent.size - self.get_size_of_siblings(siblings) - template.offset
        elif template.parent and not isinstance(template.parent.size_property,
                                                AutoSizeValueProperty):
            return template.parent.size - template.offset
        elif template.parent and template.parent.boundary > 0:
            return template.parent.boundary - template.offset
        elif template.binding_context.data:
            data = template.binding_context.data
            data.seek(0, 2)
            return data.tell()
        else:
            return 0

    def _get_multiple_of_boundary(self, value, boundary):
        if boundary == 0:
            return value
        boundary_multiplier = int(value / boundary)
        if value % boundary:
            boundary_multiplier += 1
        return boundary_multiplier * boundary

    def _get_offset_at_end_of_predecessor(self, template):
        # Need at least two children to grab previous sibling
        if template.parent and len(template.parent.children) >= 2:
            index = 0
            for (count, value) in enumerate(template.parent.children):
                if value == template:
                    index = count
                    break
            if index == 0:
                return 0
            else:
                previous_sibling = template.parent.children[index - 1]
                return (
                    previous_sibling.offset
                    + previous_sibling.size
                    + previous_sibling.padding_after
                )
        else:
            return 0

    def _get_boundary_offset_relative_to_parent(self, template):
        if template.parent:
            return self._get_boundary_offset(template.parent.offset,
                                             template.boundary)
        else:
            return 0

    def _get_boundary_offset_at_end_of_predecessor(self, template):
        offset = self._get_offset_at_end_of_predecessor(template)
        return self._get_boundary_offset(offset, template.boundary)

    def _get_boundary_offset(self, offset, boundary):
        if (boundary and offset % boundary):
            return boundary - (offset % boundary)
        else:
            return 0
