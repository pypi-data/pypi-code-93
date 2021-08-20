import threading

from stackifyapm.context.base import BaseContext


class ThreadLocalContext(BaseContext):
    thread_local = threading.local()
    thread_local.transaction = None
    stackifyapm_span_var = None

    def get_transaction(self, clear=False):
        """
        Get the transaction for the current thread.
        """
        transaction = getattr(self.thread_local, "transaction", None)
        if clear:
            self.set_transaction(None)
        return transaction

    def set_transaction(self, transaction):
        self.thread_local.transaction = transaction

    def get_span(self):
        return getattr(self.thread_local, "span", None)

    def set_span(self, span):
        self.thread_local.span = span

    def clear_span(self):
        self.set_span(None)


execution_context = ThreadLocalContext()
