from unittest import TestCase

from stackifyapm.context.base import BaseContext


class TestBaseContext(TestCase):
    def setUp(self):
        self.base_context = BaseContext()

    def test_get_transaction_should_raise(self):
        self.assertRaises(NotImplementedError, self.base_context.get_transaction)

    def test_set_transaction_should_raise(self):
        self.assertRaises(NotImplementedError, self.base_context.set_transaction, 'Test')

    def test_get_span_should_raise(self):
        self.assertRaises(NotImplementedError, self.base_context.get_span)

    def test_set_span_should_raise(self):
        self.assertRaises(NotImplementedError, self.base_context.set_span, 'Test')

    def test_clear_span_should_raise(self):
        self.assertRaises(NotImplementedError, self.base_context.clear_span)
