# -*- coding: utf-8 -*-
"""
    binalyzer_template_provider
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Template provider for Binalyzer.

    :copyright: 2020 Denis Vasilík
    :license: MIT, see LICENSE for details.
"""

name = "binalyzer_template_provider"

__tag__ = "v1.0.2"
__build__ = 112
__version__ = "{}".format(__tag__)
__commit__ = "a9973ad"

from .extension import XMLTemplateProviderExtension
from .xml import XMLTemplateParser
