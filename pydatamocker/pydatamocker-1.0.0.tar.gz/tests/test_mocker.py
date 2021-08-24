import pytest
from pydatamocker import MockTable, mocker
from tempfile import TemporaryFile
from .asserts import assert_equals
import sys


t = MockTable('T')
t.add_field('FirstName', 'first_name')
t.add_field('LastName', 'last_name')


@mocker.report_progress
def sample():
    t.sample(10)


def sample_silent():
    t.sample(10)


def test_with_config_report_progress():
    with TemporaryFile('w+') as tempfile:
        stdout = sys.stdout
        sys.stdout = tempfile
        sample()
        sample_silent()
        tempfile.flush()
        sys.stdout = stdout
        tempfile.seek(0)
        numlines = sum(1 for _ in tempfile)
        assert_equals(5, numlines, "Incorrect number of lines in the output")
