# -*- coding: utf-8 -*-
"""
    binalyzer_core.extension
    ~~~~~~~~~~~~~~~~~~~~~~~~

    This module supports the creation of Binalyzer extensions.

    :copyright: 2021 Denis Vasilík
    :license: MIT
"""


class BinalyzerExtension(object):
    """Base class for Binalyzer extensions.
    """

    def __init__(self, binalyzer=None, name=None):
        self.binalyzer = binalyzer
        self.name = name
        if self.name is None:
            raise RuntimeError('No extension name provided.')
        if binalyzer:
            self.init_binalyzer(binalyzer)
        self.init_extension()

    def init_binalyzer(self, binalyzer):
        """Registers the extension at Binalyzer.
        """
        binalyzer.add_extension(self.name, self)

    def init_extension(self):
        """When overridden, initializes the extension.
        """
        pass
