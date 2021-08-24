"""Tests for trading.datasets.utils.generic_utils."""
# pylint: disable=missing-class-docstring,missing-function-docstring

from types import ModuleType

from trading.datasets.utils import generic_utils


class TestGenericUtils:

    def test_is_generic_utils_a_module(self):
        assert isinstance(generic_utils, ModuleType)
