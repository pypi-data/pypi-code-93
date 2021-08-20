from unittest import TestCase

from stackifyapm.context.threadlocal import ThreadLocalContext
thread_local_context = ThreadLocalContext()


class GetTransactionTest(TestCase):

    def setUp(self):
        thread_local_context.thread_local.transaction = None

    def tearDown(self):
        thread_local_context.thread_local.transaction = None

    def test_should_return_none_if_empty(self):
        thread_local_context.thread_local.transaction = None
        transaction = thread_local_context.get_transaction()

        assert transaction is None

    def test_should_return_transaction_if_not_empty(self):
        thread_local_context.thread_local.transaction = 'Test'
        transaction = thread_local_context.get_transaction()

        assert transaction == 'Test'

    def test_should_not_clear_transaction_if_clear_param_is_False(self):
        thread_local_context.thread_local.transaction = 'Test'
        transaction = thread_local_context.get_transaction(clear=False)

        assert transaction == 'Test'
        assert thread_local_context.thread_local.transaction == 'Test'

    def test_should_clear_transaction_if_clear_param_is_True(self):
        thread_local_context.thread_local.transaction = 'Test'
        transaction = thread_local_context.get_transaction(clear=True)

        assert transaction == 'Test'
        assert thread_local_context.thread_local.transaction is None


class SetTransactionTest(TestCase):

    def setUp(self):
        thread_local_context.thread_local.transaction = None

    def tearDown(self):
        thread_local_context.thread_local.transaction = None

    def test_should_set_transaction(self):
        transaction = 'Transaction'
        thread_local_context.set_transaction(transaction)

        assert thread_local_context.thread_local.transaction == transaction

    def test_should_set_transaction_if_empty(self):
        transaction = None
        thread_local_context.set_transaction(transaction)

        assert thread_local_context.thread_local.transaction is None


class GetSpanTest(TestCase):

    def setUp(self):
        thread_local_context.thread_local.span = None

    def tearDown(self):
        thread_local_context.thread_local.span = None

    def test_should_return_get_span(self):
        thread_local_context.thread_local.span = 'span'
        span = thread_local_context.get_span()

        assert span == 'span'

    def test_should_return_get_span_if_empty(self):
        span = thread_local_context.get_span()

        assert span is None


class SetSpanTest(TestCase):

    def setUp(self):
        thread_local_context.thread_local.span = None

    def tearDown(self):
        thread_local_context.thread_local.span = None

    def test_should_set_span(self):
        span = 'span'
        thread_local_context.set_span(span)

        assert thread_local_context.thread_local.span == span

    def test_should_set_span_if_empty(self):
        span = None

        thread_local_context.set_span(span)

        assert thread_local_context.thread_local.span is None


class ClearSpanTest(TestCase):

    def setUp(self):
        thread_local_context.thread_local.span = None

    def tearDown(self):
        thread_local_context.thread_local.span = None

    def test_should_clear_span(self):
        thread_local_context.thread_local.span = 'span'

        thread_local_context.clear_span()

        assert thread_local_context.thread_local.span is None
