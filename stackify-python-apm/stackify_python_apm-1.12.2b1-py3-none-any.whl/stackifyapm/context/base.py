class BaseContext(object):
    def get_transaction(self, clear=False):
        raise NotImplementedError

    def set_transaction(self, transaction):
        raise NotImplementedError

    def get_span(self):
        raise NotImplementedError

    def set_span(self, span):
        raise NotImplementedError

    def clear_span(self):
        raise NotImplementedError
