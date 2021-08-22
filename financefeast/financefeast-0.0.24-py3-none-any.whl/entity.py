from types import SimpleNamespace

"""
The Response class returns 
"""

class Response(object):

    def __init__(self, payload):
        self._payload = payload

    def __repr__(self):
        """
        Returns a dict of class attributes
        """
        return "{}({!r})".format(self.__class__.__name__, self.__dict__)

    def __getattr__(self, item):
        try:
            return self._payload[item]
        except KeyError:
            return None

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value

    @property
    def data(self):
        try:
            return self._payload['data']
        except KeyError:
            return []

    @property
    def all(self):
        try:
            return SimpleNamespace(**self._payload)
        except KeyError:
            return []
