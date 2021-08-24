"""Tests for trading.datasets.utils.datetime_utils."""
# pylint: disable=missing-class-docstring,missing-function-docstring

import pytest

from trading.datasets.utils import datetime_utils


@pytest.fixture(name='datetime', scope="class")
def fixture_datetime():
    return datetime_utils.get_datetime('2021-01-01 00:00:00+00:00')


class TestDateTimeUtils:

    def test_iso8601_conversion(self, datetime):
        assert datetime_utils.get_iso8601(
            514862627000) == '1986-04-26T01:23:47.000Z'
        assert datetime_utils.get_iso8601(
            514862627559) == '1986-04-26T01:23:47.559Z'
        assert datetime_utils.get_iso8601(
            514862627062) == '1986-04-26T01:23:47.062Z'
        assert datetime_utils.get_iso8601(
            datetime) == '2021-01-01T00:00:00.000Z'

    def test_seconds_conversion(self, datetime):
        assert datetime_utils.get_seconds(514862627000) == 514862627.000
        assert datetime_utils.get_seconds(514862627559) == 514862627.559
        assert datetime_utils.get_seconds(514862627062) == 514862627.062
        assert datetime_utils.get_seconds(datetime) == 1609459200.000

    def test_milliseconds_conversion(self, datetime):
        assert datetime_utils.get_milliseconds(514862627000) == 514862627000
        assert datetime_utils.get_milliseconds(514862627559) == 514862627559
        assert datetime_utils.get_milliseconds(514862627062) == 514862627062
        assert datetime_utils.get_milliseconds(datetime) == 1609459200000
