# -*- coding: utf-8 -*-
"""
    binalyzer_core.modify
    ~~~~~~~~~~~~~~~~~~~~~

    This module implements modifiation functions for templates.

    :copyright: 2021 Denis Vasilík
    :license: MIT
"""
from binalyzer_core.binding import (
    PinnedBindingContext,
    BackedBindingContext,
)


def transform(source_template, destination_template, additional_data={}):
    project(source_template, destination_template, additional_data)
    aggregate(destination_template)


def project(source_template, destination_template, additional_data={}):
    _split(destination_template)

    existing_leaves = [(source_leave, destination_leave)
                       for source_leave in source_template.leaves
                       for destination_leave in destination_template.leaves
                       if _is_path_equal(source_leave.path, destination_leave.path)]

    for (source_leave, destination_leave) in existing_leaves:
        extension_size = 0
        overriden_size = 0
        if destination_leave.size >= 0:
            overriden_size = destination_leave.size
        if destination_leave.size > source_leave.size:
            extension_size = destination_leave.size - source_leave.size
        destination_leave.value = (
            source_leave.value + bytes([0] * extension_size))
        if overriden_size:
            destination_leave.size = overriden_size

    _bind(_diff(source_template, destination_template), additional_data)


def aggregate(template):
    _aggregate(template, BackedBindingContext(template, propagate=False))


def _split(template):
    template._binding_context = PinnedBindingContext(template, propagate=False)
    for child in template.children:
        _split(child)


def _aggregate(template, binding_context):
    temp_value = None
    if template.is_leaf:
        temp_value = template.value
    template._binding_context = binding_context
    if temp_value:
        template.value = temp_value
    for child in template.children:
        _aggregate(child, binding_context)


def _diff(source_template, destination_template):
    return (destination_leave
            for destination_leave in destination_template.leaves
            if destination_leave.name not in
            (source_leave.name for source_leave in source_template.leaves))


def _bind(templates, data_template_map):
    for template in templates:
        if template.name in list(data_template_map.keys()):
            template.value = data_template_map[template.name]
        else:
            template.value = bytes([0] * template.size)


def _is_path_equal(source_path, dest_path):
    source_path_str = ''
    for s in source_path:
        source_path_str += s.name
        source_path_str += s.separator

    dest_path_str = ''
    for s in dest_path:
        dest_path_str += s.name
        dest_path_str += s.separator

    return source_path_str == dest_path_str
