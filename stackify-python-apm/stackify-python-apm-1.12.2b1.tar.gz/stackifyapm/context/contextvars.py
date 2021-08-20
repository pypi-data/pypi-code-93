from __future__ import absolute_import

import contextvars

from stackifyapm.context.base import BaseContext


class ContextVarsContext(BaseContext):
    stackifyapm_transaction_var = contextvars.ContextVar("stackifyapm_transaction_var")
    stackifyapm_span_var = contextvars.ContextVar("stackifyapm_span_var")

    def get_transaction(self, clear=False):
        try:
            transaction = self.stackifyapm_transaction_var.get()
            if clear:
                self.set_transaction(None)
            return transaction
        except LookupError:
            return None

    def set_transaction(self, transaction):
        self.stackifyapm_transaction_var.set(transaction)

    def get_span(self):
        try:
            return self.stackifyapm_span_var.get()
        except LookupError:
            return None

    def set_span(self, span):
        self.stackifyapm_span_var.set(span)

    def clear_span(self):
        self.set_span(None)


execution_context = ContextVarsContext()
