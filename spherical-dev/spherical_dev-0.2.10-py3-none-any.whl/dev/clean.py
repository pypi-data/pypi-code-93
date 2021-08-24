import pathlib
import shutil

import invoke


@invoke.task
def clean(ctx):
    """Clean up the current directory from temporary files"""
    for path in (
        '.coverage',
        '.eggs',
        '.pytest_cache',
        'build',
        'dist',
        'htmlcov',
    ):
        path = pathlib.Path(path)
        if path.is_dir():
            shutil.rmtree(path)
        elif path.is_file():
            path.unlink()
    for path in pathlib.Path().rglob('*.egg-info'):
        shutil.rmtree(path)
    for path in pathlib.Path().glob('*.whl'):
        path.unlink()
