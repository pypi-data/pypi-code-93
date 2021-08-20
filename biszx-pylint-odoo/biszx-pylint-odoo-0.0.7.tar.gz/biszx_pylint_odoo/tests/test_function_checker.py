import pytest
import os
from functools import reduce
from pylint.lint import Run

from .. import settings, messages

DEFAULT_OPTIONS = [
    '--load-plugins=biszx_pylint_odoo', '--reports=no', '--msg-template='
    '"{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}"',
    '--output-format=colorized', '--rcfile=%s' % os.devnull,
]


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
    cmd = DEFAULT_OPTIONS + extra_options + paths
    try:
        res = Run(cmd, do_exit=False)  # pylint 2
    except TypeError:
        res = Run(cmd, exit=False)  # pylint 1
    return res


def test_function_checker():
    pylint_res = run_pylint(
        [f'./{settings.TEST_DATA_PATH}/function_checker/wrong.py'])
    real_errors = pylint_res.linter.stats['by_msg']
    assert real_errors == {
        'biszx-domain-func-name': 1,
        'biszx-default-func-name': 2,
        'biszx-search-func-name': 1,
        'biszx-compute-func-name': 1,
        'biszx-onchange-func-name': 1,
        'biszx-constrains-func-name': 1
    }
