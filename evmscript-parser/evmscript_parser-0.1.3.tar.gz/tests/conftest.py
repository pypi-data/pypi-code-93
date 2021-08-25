"""Settings for tests."""
import pytest

from typing import List
from functools import partial

from examples import Parsing, ABIEtherscan


def _parametrize(
        metafunc, fixture_name: str, cases: List
) -> None:
    if fixture_name in metafunc.fixturenames:
        if hasattr(_parametrize, fixture_name):
            cases, names = getattr(
                _parametrize, fixture_name
            )

        else:
            names = [
                f'case_{ind}'
                for ind in range(len(cases))
            ]

            setattr(
                _parametrize, fixture_name, (cases, names)
            )

        metafunc.parametrize(
            fixture_name, cases, ids=names
        )


def pytest_generate_tests(metafunc):
    """Parametrize tests."""
    parametrize = partial(_parametrize, metafunc)
    for fixture_name, cases in [
        ('positive_example', Parsing.positive_examples),
        ('negative_example', Parsing.negative_examples),
        ('abi_positive_example', ABIEtherscan.positive_examples)
    ]:
        parametrize(fixture_name, cases)


def pytest_addoption(parser):
    """Add CLI parameters for tests."""
    parser.addoption(
        '--apikey', type=str,
        default=None, help='API key for Etherscan.'
    )


@pytest.fixture()
def api_key(pytestconfig) -> str:
    """Return apikey from CLI parameters."""
    return pytestconfig.getoption('apikey')
