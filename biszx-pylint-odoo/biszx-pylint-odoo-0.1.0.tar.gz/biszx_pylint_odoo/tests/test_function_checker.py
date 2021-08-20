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
        messages.FUNCTION_CHECKER_MSGS.values(),
        ''
    )[1:]}''',
]


def run_pylint(paths, extra_options=None):
    if extra_options is None:
        extra_options = DEFAULT_EXTRA_OPTIONS
    cmd = settings.DEFAULT_OPTIONS + extra_options + paths
    return Run(cmd, do_exit=False)


def test_function_checker():
    pylint_res = run_pylint(
        [f'./{settings.TEST_DATA_PATH}/function_checker_data.py'])
    real_errors = pylint_res.linter.stats['by_msg']
    assert real_errors == {
        'biszx-domain-func-name': 1,
        'biszx-default-func-name': 2,
        'biszx-search-func-name': 1,
        'biszx-compute-func-name': 2,
        'biszx-onchange-func-name': 1,
        'biszx-constrains-func-name': 1
    }
