import pytest
import os
from functools import reduce
from pylint.lint import Run

from .. import messages
from . import settings


DEFAULT_EXTRA_OPTIONS = [
    '--disable=all',
    f'''--enable={reduce(
        lambda a, v: f'{a},{v[1]}',
        messages.FIELD_CHECKER_MSGS.values(),
        ''
    )[1:]}''',
]


def run_pylint(paths, extra_options=None):
    if extra_options is None:
        extra_options = DEFAULT_EXTRA_OPTIONS
    cmd = settings.DEFAULT_OPTIONS + extra_options + paths
    return Run(cmd, do_exit=False)


def test_field_checker():
    pylint_res = run_pylint(
        [f'./{settings.TEST_DATA_PATH}/field_checker_data.py'])
    real_errors = pylint_res.linter.stats['by_msg']
    assert real_errors == {
        'biszx-relation2one-field-name': 1,
        'biszx-relation2many-field-name': 2,
        'biszx-boolean-field-name': 1,
        'biszx-date-field-name': 1,
        'biszx-datetime-field-name': 1,
    }
