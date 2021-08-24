# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from sys import version_info

from contrast.extern.isort import stdlibs


_version_string = "py{0[0]}{0[1]}".format(version_info)
_stdlib_modules = getattr(stdlibs, _version_string).stdlib


def is_stdlib_module(module_name):
    """
    Returns True if module_name belongs to standard library module, False otherwise.

    NOTE: 'test' is included in _stdlib_modules so if we're testing this,
    we cannot pass in a module that starts with test.file...
    """
    top_module_name = module_name.split(".")[0]
    return top_module_name in _stdlib_modules
