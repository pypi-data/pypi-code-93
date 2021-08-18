from despik_package.despik_package_v1 import despik_package
import pytest


@pytest.mark.parametrize("a, expected_results", [('sdfg', ['SDFG']),
                                                    (['sdfg', 'pragf'], ['SDFG', 'PRAGF'])])
def test_isupper(a, expected_results):
    assert despik_package.ticker_upper(a) == expected_results









