from requests import Session


class SampleClass3(object):
    def __init__(self):
        self._session = Session()

    def some_method(self):
        self._session.get("http://test.test")
