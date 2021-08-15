""" Test module. Auto pytest that can be started in IDE or with::

    python -m pytest

in terminal in tests folder.
"""
#%%

from pathlib import Path
import os
import inspect
import shutil
import sys

import mylogging

mylogging.config.COLOR = 0

# Find paths and add to sys.path to be able to import local modules
test_path = Path(os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)).parent
ROOT_PATH = test_path.parent

if ROOT_PATH not in sys.path:
    sys.path.insert(0, ROOT_PATH.as_posix())

import mypythontools


def test_utils():

    shutil.rmtree(ROOT_PATH / "build", ignore_errors=True)
    if (ROOT_PATH / "docs" / "source" / "modules.rst").exists():
        (ROOT_PATH / "docs" / "source" / "modules.rst").unlink()  # missing_ok=True from python 3.8 on...

    mypythontools.paths.set_paths()
    mypythontools.utils.sphinx_docs_regenerate()
    mypythontools.utils.get_version()

    # TODO test if correct


def test_build():

    # Build app with pyinstaller example
    mypythontools.paths.set_paths(set_ROOT_PATH=test_path)
    mypythontools.build.build_app(main_file="app.py", console=True, debug=True, cleanit=False)
    mypythontools.paths.set_paths()

    assert (test_path / "dist").exists()

    shutil.rmtree(ROOT_PATH / "tests" / "build")
    shutil.rmtree(ROOT_PATH / "tests" / "dist")


if __name__ == "__main__":
    # test_it()
    pass
