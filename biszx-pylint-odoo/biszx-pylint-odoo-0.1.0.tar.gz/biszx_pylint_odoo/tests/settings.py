import os

TEST_DATA_PATH = 'biszx_pylint_odoo/tests/data'

DEFAULT_OPTIONS = [
    '--load-plugins=biszx_pylint_odoo', '--reports=no', '--msg-template='
    '"{path}:{line}: [{msg_id}({symbol})]"',
    '--output-format=colorized', '--rcfile=%s' % os.devnull,
]
