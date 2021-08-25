import pytest

import uri_handler.uri_functions

from conftest import uribase_fixtures_to_test


def test_tests():
    """dummy test"""


def test_uri_functions_decorator():
    pass


@pytest.mark.parametrize(
    "uri_base_fixture", uribase_fixtures_to_test)
def test_readwrite_uri(uri_base_fixture, request):
    uri = request.getfixturevalue(uri_base_fixture)

    test_str = "test"
    test_b = test_str.encode("UTF-8")

    test_uri = uri_handler.uri_functions.uri_join(
        uri, "test_data")

    uri_handler.uri_functions.uri_writebytes(
        test_uri, test_b)

    r = uri_handler.uri_functions.uri_readbytes(
        test_uri)

    assert r == test_b
    assert r.decode("UTF-8") == test_str
