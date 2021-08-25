# -*- coding: utf-8 -*-
"""
    test.memory.test_DummyMemoryPersistence
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Tests for memory persistence
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from .DummyMemoryPersistence import DummyMemoryPersistence
from ..DummyPersistenceFixture import DummyPersistenceFixture


class TestDummyMemoryPersistence:

    @classmethod
    def setup_class(cls):
        cls.persistence = DummyMemoryPersistence()
        cls.fixture = DummyPersistenceFixture(cls.persistence)

    def setup_method(self, method):
        self.persistence.clear(None)

    def test_crud_operations(self):
        self.fixture.test_crud_operations()

    def test_batch_operations(self):
        self.fixture.test_batch_operations()
