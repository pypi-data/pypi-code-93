#%%
import shutil
from pathlib import Path
import sys

sys.path.insert(0, Path(__file__).parents[1])

import mypythontools

# Find paths and add to sys.path to be able to import local modules
mypythontools.tests.setup_tests()

from conftest import ROOT_PATH, TEST_PATH


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
    mypythontools.paths.set_paths(set_ROOT_PATH=TEST_PATH)
    mypythontools.build.build_app(main_file="app.py", console=True, debug=True, cleanit=False)
    mypythontools.paths.set_paths()

    assert (TEST_PATH / "dist").exists()

    shutil.rmtree(ROOT_PATH / "tests" / "build")
    shutil.rmtree(ROOT_PATH / "tests" / "dist")


if __name__ == "__main__":
    # test_it()
    pass


mypythontools.paths.set_root()
