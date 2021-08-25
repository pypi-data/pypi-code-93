# -*- coding: utf-8 -*-
"""
    test.file.DummyFilePersistence
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Dummy file persistence implementation

    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services3_data.persistence import JsonFilePersister
from ..persistence.DummyMemoryPersistence import DummyMemoryPersistence


class DummyFilePersistence(DummyMemoryPersistence):
    _persister = None

    def __init__(self, path=None):
        super(DummyFilePersistence, self).__init__()

        self._persister = JsonFilePersister(path)
        self._loader = self._persister
        self._saver = self._persister

    def configure(self, config):
        super(DummyFilePersistence, self).configure(config)
        self._persister.configure(config)
