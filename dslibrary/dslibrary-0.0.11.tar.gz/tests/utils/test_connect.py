import unittest

from dslibrary.utils.connect import _process_params


class TestConnect(unittest.TestCase):
    def test__process_params(self):
        r = _process_params("mysql://u:p@host:1234/database", extra=1)
        assert r == {
            'host': 'host',
            'port': 1234,
            'database': 'database',
            'username': 'u',
            'password': 'p',
            'extra': 1
        }, r
        r = _process_params("xyz://u@host")
        assert r == {
            'host': 'host',
            'port': None,
            'database': '',
            'username': 'u',
            'password': ''
        }, r
        r = _process_params("sqlite:path/to/file")
        assert r == {
            'host': '',
            'port': None,
            'database': 'path/to/file',
            'username': '',
            'password': ''
        }, r
        r = _process_params("x://host/db", database="db2")
        assert r == {
            'host': 'host',
            'port': None,
            'database': 'db2',
            'username': '',
            'password': ''
        }, r


