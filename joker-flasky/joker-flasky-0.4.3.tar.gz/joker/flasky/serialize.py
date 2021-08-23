#!/usr/bin/env python3
# coding: utf-8

import warnings

from joker.flasky.viewutils import JSONEncoderPlus, jsonp
from volkanic.utils import indented_json_dumps, indented_json_print

_warning = """\
joker.flasky.serialize is deprecated, please consider use
- joker.flasky.viewutils.JSONEncoderPlus
- joker.flasky.viewutils.jsonp
- volkanic.utils.indented_json_dumps
- volkanic.utils.indented_json_print
"""

warnings.warn(
    _warning,
    DeprecationWarning
)

__all__ = [
    'JSONEncoderPlus',
    'jsonp',
    'indented_json_dumps',
    'indented_json_print',
]
