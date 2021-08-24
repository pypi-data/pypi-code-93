"""Tests for trading.datasets.utils.cache_utils."""
# pylint: disable=missing-class-docstring,missing-function-docstring

import os

from trading.datasets.utils import cache_utils


class TestCacheUtils:

    def test_default_cache_dir_notebook_environment(self):
        assert '.cache' not in str(
            cache_utils._default_cache_dir(exposed=True))  # pylint: disable=protected-access

    def test_default_cache_dir_non_notebook(self):
        assert '.cache' in str(
            cache_utils._default_cache_dir(exposed=False))  # pylint: disable=protected-access

    def test_default_cache_dir_os_environment(self):
        os.environ['TDS_CACHE_DIR'] = 'some/directory/'
        cache_dir = str(
            cache_utils._default_cache_dir())  # pylint: disable=protected-access

        assert cache_dir.startswith('some')
        assert 'directory' in cache_dir
