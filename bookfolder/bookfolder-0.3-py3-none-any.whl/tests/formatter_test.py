"""
Tests for formatter classes
"""

import pytest

from bookfolder.formatter import CSVFormatter
from bookfolder.sheet import Sheet


@pytest.fixture
def simple_sheets_fx():
    """
    Return a list of three Sheet objects.
    """
    measurement_interval = 0.1
    return [
        Sheet([10, 15, 20],
              measurement_interval=measurement_interval,
              page_number=1),
        Sheet([12, 14, 25],
              measurement_interval=measurement_interval,
              page_number=3),
        Sheet([13, 14, 30],
              measurement_interval=measurement_interval,
              page_number=5),
        ]


# tests should have descriptive enough names
# pylint: disable=missing-function-docstring

# pylint doesn't recognize fixtures
# pylint: disable=redefined-outer-name

def test_csv_header_present():
    formatter = CSVFormatter([])
    assert "page; cut and fold point locations (cm)" in formatter.format()


def test_csv_formatter_produces_right_number_of_lines(simple_sheets_fx):
    formatter = CSVFormatter(simple_sheets_fx)
    assert len(formatter.format().split("\n")) == 4


def test_csv_formatter_produces_right_data_contents(simple_sheets_fx):
    formatter = CSVFormatter(simple_sheets_fx)
    assert formatter.format() == (
        "page; cut and fold point locations (cm)\n"
        "1; 0.1; 0.15; 0.2\n"
        "3; 0.12; 0.14; 0.25\n"
        "5; 0.13; 0.14; 0.3")
