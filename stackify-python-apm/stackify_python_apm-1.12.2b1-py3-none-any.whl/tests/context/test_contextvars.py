from unittest import TestCase
from unittest import SkipTest

try:
    from stackifyapm.context.contextvars import ContextVarsContext
except Exception:
    raise SkipTest('Skipping due to version incompatibility')

context_vars_context = ContextVarsContext()


class GetTransactionTest(TestCase):

    def setUp(self):
        context_vars_context.stackifyapm_transaction_var.set(None)

    def tearDown(self):
        context_vars_context.stackifyapm_transaction_var.set(None)

    def test_should_return_none_if_empty(self):
        context_vars_context.stackifyapm_transaction_var.set(None)
        transaction = context_vars_context.get_transaction()

        assert transaction is None

    def test_should_return_transaction_if_not_empty(self):
        context_vars_context.stackifyapm_transaction_var.set('Test')
        transaction = context_vars_context.get_transaction()

        assert transaction == 'Test'

    def test_should_not_clear_transaction_if_clear_param_is_False(self):
        context_vars_context.stackifyapm_transaction_var.set('Test')
        transaction = context_vars_context.get_transaction(clear=False)

        assert transaction == 'Test'
        assert context_vars_context.stackifyapm_transaction_var.get() == 'Test'

    def test_should_clear_transaction_if_clear_param_is_True(self):
        context_vars_context.stackifyapm_transaction_var.set('Test')
        transaction = context_vars_context.get_transaction(clear=True)

        assert transaction == 'Test'
        assert context_vars_context.stackifyapm_transaction_var.get() is None


class SetTransactionTest(TestCase):

    def setUp(self):
        context_vars_context.stackifyapm_transaction_var.set(None)

    def tearDown(self):
        context_vars_context.stackifyapm_transaction_var.set(None)

    def test_should_set_transaction(self):
        transaction = 'Transaction'
        context_vars_context.set_transaction(transaction)

        assert context_vars_context.stackifyapm_transaction_var.get() == transaction

    def test_should_set_transaction_if_empty(self):
        transaction = None
        context_vars_context.set_transaction(transaction)

        assert context_vars_context.stackifyapm_transaction_var.get() is None


class GetSpanTest(TestCase):

    def setUp(self):
        context_vars_context.stackifyapm_span_var.set(None)

    def tearDown(self):
        context_vars_context.stackifyapm_span_var.set(None)

    def test_should_return_get_span(self):
        context_vars_context.stackifyapm_span_var.set('span')
        span = context_vars_context.get_span()

        assert span == 'span'

    def test_should_return_get_span_if_empty(self):
        span = context_vars_context.get_span()

        assert span is None


class SetSpanTest(TestCase):

    def setUp(self):
        context_vars_context.stackifyapm_span_var.set(None)

    def tearDown(self):
        context_vars_context.stackifyapm_span_var.set(None)

    def test_should_set_span(self):
        span = 'span'
        context_vars_context.set_span(span)

        assert context_vars_context.stackifyapm_span_var.get() == span

    def test_should_set_span_if_empty(self):
        span = None

        context_vars_context.set_span(span)

        assert context_vars_context.stackifyapm_span_var.get() is None


class ClearSpanTest(TestCase):

    def setUp(self):
        context_vars_context.stackifyapm_span_var.set(None)

    def tearDown(self):
        context_vars_context.stackifyapm_span_var.set(None)

    def test_should_clear_span(self):
        context_vars_context.stackifyapm_span_var.set('span')

        context_vars_context.clear_span()

        assert context_vars_context.stackifyapm_span_var.get() is None
