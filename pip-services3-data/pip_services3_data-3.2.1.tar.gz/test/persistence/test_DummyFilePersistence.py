# -*- coding: utf-8 -*-
"""
    test.file.test_DummyFilePersistence
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Tests for file persistence
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from .DummyFilePersistence import DummyFilePersistence
from ..DummyPersistenceFixture import DummyPersistenceFixture


class TestDummyFilePersistence:

    @classmethod
    def setup_class(cls):
        cls.persistence = DummyFilePersistence("./data/dummies.json")
        cls.fixture = DummyPersistenceFixture(cls.persistence)

    def setup_method(self, method):
        self.persistence.clear(None)

    def test_crud_operations(self):
        self.fixture.test_crud_operations()

    def test_load_data(self):
        self.persistence.load(None)

    def test_batch_operations(self):
        self.fixture.test_batch_operations()
