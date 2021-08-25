import os
from django.test import TestCase
from ievv_opensource.utils import virtualenvutils
from unittest import mock


class TestVirtualenvUtils(TestCase):
    def test_is_in_virtualenv_true(self):
        class MockSys:
            real_prefix = '/something'
        with mock.patch('ievv_opensource.utils.virtualenvutils.sys', MockSys):
            self.assertTrue(virtualenvutils.is_in_virtualenv())

    def test_is_in_virtualenv_false(self):
        class MockSys:
            pass
        with mock.patch('ievv_opensource.utils.virtualenvutils.sys', MockSys):
            self.assertFalse(virtualenvutils.is_in_virtualenv())

    def test_get_virtualenv_directory_not_in_virtualenv(self):
        class MockSys:
            pass
        with mock.patch('ievv_opensource.utils.virtualenvutils.sys', MockSys):
            with self.assertRaises(OSError):
                virtualenvutils.get_virtualenv_directory()

    def test_get_virtualenv_directory_is_in_virtualenv(self):
        class MockSys:
            real_prefix = '/something'
            prefix = '/virtual'
        with mock.patch('ievv_opensource.utils.virtualenvutils.sys', MockSys):
            self.assertEqual('/virtual', virtualenvutils.get_virtualenv_directory())

    def test_add_virtualenv_bin_directory_to_path(self):
        class MockSys:
            real_prefix = '/real'
            prefix = '/virtual'
        mockenviron = {'PATH': ''}
        with mock.patch('ievv_opensource.utils.virtualenvutils.sys', MockSys):
            with mock.patch('ievv_opensource.utils.virtualenvutils.os.environ',
                            mockenviron):
                virtualenvutils.add_virtualenv_bin_directory_to_path()
        self.assertEqual('{}/virtual/bin'.format(os.pathsep),
                         mockenviron['PATH'])
