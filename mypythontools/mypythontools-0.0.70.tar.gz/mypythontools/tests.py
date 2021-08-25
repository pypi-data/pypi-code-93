import subprocess
from pathlib import Path
import sys
import warnings
import platform
import shutil

import mylogging

from . import paths


def setup_tests(matplotlib_test_backend=False):
    """Add paths to be able to import local version of library as well as other test files.

    Value Mylogging.config.COLOR = 0 changed globally.

    Note:
        Function expect `tests` folder on root. If not, test folder will not be added to sys path and
        imports from tests will not work.

    Args:
        matplotlib_test_backend (bool, optional): If using matlplotlib, it need to be
            closed to continue tests. Change backend to agg. Defaults to False.
    """
    mylogging.config.COLOR = 0

    paths.set_root()

    # Find paths and add to sys.path to be able to import local modules
    test_dir_path = paths.ROOT_PATH / "tests"

    if test_dir_path not in sys.path:
        sys.path.insert(0, test_dir_path.as_posix())

    if matplotlib_test_backend:
        import matplotlib

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            matplotlib.use("agg")


def run_tests(
    test_path=None,
    test_coverage=True,
    stop_on_first_error=True,
    use_virutalenv=True,
    requirements=None,
    verbose=False,
    extra_args=[],
):
    """Run tests. If any test fails, raise an error.

    Args:
        test_path ((str, pathlib.Path), optional): If None, ROOT_PATH is used. ROOT_PATH is necessary if using doctests
            'Tests' folder not works for doctests in modules. Defaults to None.
        test_coverage (bool, optional): Whether run test coverage plugin. If True, pytest-cov must be installed. Defaults to True
        stop_on_first_error (bool, optional): Whether stop on first error. Defaults to True
        use_virutalenv (bool, optional): Whether run new virtualenv and install all libraries from requirements.txt. Defaults to True
        requirements ((str, pathlib.Path, list), optional): If using `use_virutalenv` define what libraries will be installed.
            If None, autodetected. Can also be a list of more files e.g `["requirements.txt", "requirements_dev.txt"]`. Defaults to None.
        verbose (bool, optional): Whether print detailes on errors or keep silent. If False, parameters `-q and `--tb=no` are added.
            Defaults to False.
        extra_args (list, optional): List of args passed to pytest. Defaults to []

    Raises:
        Exception: If any test fail, it will raise exception (git hook do not continue...).

    Note:
        If not using with utils.push_pipeline, paths.set_paths().

        By default args to quiet mode and no traceback are passed. Usually this just runs automatic tests. If some of them fail,
        it's further analyzed in some other tool in IDE.
    """

    if not test_path:
        test_path = paths.ROOT_PATH  # Because of doctest, root used, not tests folder

    if not test_coverage:
        pytest_args = [test_path.as_posix()]
    else:
        pytest_args = [
            test_path.as_posix(),
            "--cov",
            paths.APP_PATH.as_posix(),
            "--cov-report",
            "xml:.coverage.xml",
        ]

    if stop_on_first_error:
        extra_args.append("-x")

    if not verbose:
        extra_args.append("-q")
        extra_args.append("--tb=no")

    complete_args = ["pytest", *pytest_args, *extra_args]

    test_command = " ".join(complete_args)

    if use_virutalenv:
        if not requirements:
            default_requirements_path = paths.ROOT_PATH / "requirements.txt"
            requirements = [
                default_requirements_path
                if default_requirements_path.exists()
                else paths.paths.find_path("requirements.txt")
            ]

        requirements = [requirements] if not isinstance(requirements, list) else requirements

        requirements_command = " && ".join(
            [f"pip install --upgrade -r {Path(req).as_posix()}" for req in requirements]
        )

        if platform.system() == "Windows":
            subprocess.run("virtualenv venv_test")
            activate_command = r"venv_test\Scripts\activate.bat"
        else:
            subprocess.run("python3 -m virtualenv venv_test")
            activate_command = "source venv_test/bin/activate"

        command_venv_prefix = f"{activate_command} && {requirements_command} && pip install pytest &&"

        test_command = command_venv_prefix + test_command

    pytested = subprocess.run(test_command, shell=True)

    if test_coverage and Path(".coverage").exists():
        Path(".coverage").unlink()

    if use_virutalenv:
        virtualenv_path = paths.ROOT_PATH / "venv_test"
        shutil.rmtree(virtualenv_path.as_posix())

    if pytested.returncode == 1:
        raise RuntimeError(mylogging.return_str("Pytest failed"))


def test_readme(readme_path=None, test_folder_path=None):
    """Run python scripts from README.md

    Args:
        readme_path ((str, pathlib.Path), optional): If None, autodetected (README.md or readme.md on root). Defaults to None.
        test_folder_path ((str, pathlib.Path), optional): If None, autodetected (if ROOT_PATH / tests). Defaults to None.

    Raises:
        RuntimeError: If any test fails.
        FileNotFoundError: If Readme not found.

    Note:
        Only blocks with python defined syntax will be evaluated. Example:

            ```python
            import numpy
            ```

        First generate test file manually and control if test file generated as supposed with::

            phmdoctest path_to_readme/README.md --outfile path_to_project/tests/test_readme_generated.py

        If you want to import modules and use some global variables, add `<!--phmdoctest-setup-->` this directive above
        block with setup code.
        If you want to skip some test, add `<!--phmdoctest-mark.skip-->`
    """
    if not paths.ROOT_PATH:
        paths.set_root()

    if not readme_path:
        if (paths.ROOT_PATH / "README.md").exists():
            readme_path = paths.ROOT_PATH / "README.md"

        elif (paths.ROOT_PATH / "readme.md").exists():
            readme_path = paths.ROOT_PATH / "README.md"

    else:
        readme_path = Path(readme_path)

    if not readme_path.exists():
        raise FileNotFoundError(mylogging.return_str("Readme not found."))

    if not test_folder_path:
        test_folder_path = paths.ROOT_PATH / "tests" / "test_readme_generated.py"

    args = ["phmdoctest", readme_path.as_posix(), "--outfile", test_folder_path.as_posix()]
    subprocess.call(args)

    try:
        run_tests(test_folder_path, False)
    except Exception:
        raise RuntimeError(
            mylogging.return_str(
                f"README tests failed. Generate tests in your test folder with \n\n{' '.join(args)}\n\nand run and analyze generated pytest tests to see details."
            )
        )
    finally:
        if test_folder_path.exists():
            test_folder_path.unlink()


def deactivate_test_settings():
    """Sometimes you want to run test just in normal mode (enable plots etc.). Usually at the end of test file in `if __name__ = "__main__":` block."""
    mylogging.config.COLOR = 1

    if "matplotlib" in sys.modules:

        import matplotlib
        import importlib

        importlib.reload(matplotlib)
