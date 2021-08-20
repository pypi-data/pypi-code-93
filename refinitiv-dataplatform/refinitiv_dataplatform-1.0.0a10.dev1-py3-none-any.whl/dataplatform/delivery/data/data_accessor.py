# coding: utf8

__all__ = ["DataAccessor"]


class DataAccessor(object):
    class Params(object):
        def __init__(self):
            self._session = None
            self.endpoint = None
            self._on_response = None

        def session(self, session):
            self._session = session
            return self

        def on_response(self, on_response):
            self._on_response = on_response
            return self

    def __init__(self):
        self._params = None

    def get_data(self, data_accessor_param):
        pass
