"""
Allow to deploy project.
Possible destinations: PYPI.

Check `deploy_to_pypi` function docs for how to use it.

Usually this function is not called manually, but it's a part of `push_pipeline` from utils.

Check utils docs where is described, how to use VS Code Task to be able to optionally test, push and deploy
with tasks (one button click).
"""
import subprocess
import os
import shutil

import mylogging

from . import paths


def deploy_to_pypi(setup_path=None):
    """Publish python library to Pypi. Username and password are set
    with env vars `TWINE_USERNAME` and `TWINE_PASSWORD`.

    Note:
        You need working `setup.py` file. If you want to see example, try the one from project-statrer on

        https://github.com/Malachov/mypythontools/blob/master/content/project-starter/setup.py

    Args:
        setup_path((str, pathlib.Path), optional): Function suppose, that there is a setup.py somewhere in cwd.
            If not, pass path to setup.py. Defaults to None.
    """

    usr = os.environ.get("TWINE_USERNAME")
    pas = os.environ.get("TWINE_PASSWORD")

    if not usr or not pas:
        raise KeyError(
            mylogging.return_str("Setup env vars TWINE_USERNAME and TWINE_PASSWORD to use deploy.")
        )

    setup_path = paths.ROOT_PATH if not setup_path else setup_path

    setup_py_path = setup_path / "setup.py"

    if not setup_py_path.exists():
        setup_py_path = paths.find_path("setup.py", exclude=["node_modules"])
        setup_path = setup_py_path.parent

        if not (setup_path / "setup.py").exists():
            raise FileNotFoundError(
                mylogging.return_str("Setup.py file not found. Setup `setup_path` param.")
            )

    try:
        shutil.rmtree(setup_path / "dist")
        shutil.rmtree(setup_path / "build")

    except Exception:
        pass

    build_command = "python setup.py sdist bdist_wheel"

    subprocess.run(build_command.split(), cwd=setup_path, shell=True, check=True)

    subprocess.run(
        [
            "twine",
            "upload",
            "-u",
            os.environ["TWINE_USERNAME"],
            "-p",
            os.environ["TWINE_PASSWORD"],
            "dist/*",
        ],
        cwd=setup_path,
        shell=True,
        check=True,
    )

    shutil.rmtree(setup_path / "dist")
    shutil.rmtree(setup_path / "build")
