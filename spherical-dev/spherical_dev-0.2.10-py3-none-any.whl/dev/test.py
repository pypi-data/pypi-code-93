import os
import pathlib
import webbrowser

import invoke


@invoke.task(
    help={
        'coverage': 'Collect coverage report and show it in browser.',
        'deprecations': 'Show python warnings.',
        'verbose': 'Increase verbosity.',
        'pdb': 'Invoke the Python debugger on every failure of tests.',
        'ipython': 'Use ipython in tests debug.',
        'key': 'Only run tests which match the given `key`.',
        'skip-capture': 'Disable all capturing.',
    },
)
def test(
    ctx,
    coverage=False,
    deprecations=False,
    verbose=False,
    pdb=False,
    ipython=False,
    key=None,
    skip_capture=False,
):
    """Execute tests"""
    cwd = os.getcwd()
    ctx.run(
        ' '.join((
            'pytest',
            *(coverage and (f'--cov={cwd}', '--cov-report=html') or ()),
            *(verbose and ('-vv',) or ()),
            *(pdb and ('--pdb',) or ()),
            *(ipython and ('--pdbcls=spherical.dev.debugger:Debugger',) or ()),
            *(key and (f'-k {key}',) or ()),
            *(skip_capture and ('-s',) or ()),
        )),
        pty=True,
        env={} if deprecations else {
            'PYTHONWARNINGS': (
                'default,'
                'ignore::DeprecationWarning,'
                'ignore::ResourceWarning'
            ),
        },
    )
    report_index = pathlib.Path('htmlcov/index.html').resolve()
    if coverage:
        webbrowser.open(f'file:{report_index}')
