"""
Module where you can configure and process paths.
"""
from pathlib import Path
import sys

import mylogging


# Root is usually current working directory, if not, use `set_paths` function.
ROOT_PATH = None  # Path where all project is (docs, tests...)
APP_PATH = None  # Folder where python scripts are (and __init__.py)
INIT_PATH = None  # Path to __init__.py


def set_paths(set_ROOT_PATH=None, set_INIT_PATH=None):
    """Parse python project application structure, add paths to sys.path and save
    to paths module variables.

    Get next paths:

        ROOT_PATH - Folder where all project is (docs, tests...)
        APP_PATH - Folder where python scripts are (and __init__.py)
        INIT_PATH - Path to __init__.py

    Args:
        set_ROOT_PATH ((str, pathlib.Path), optional): Path to project root where tests and docs folder are.
            If None, then cwd (current working directory) is used. Defaults to None.
        set_INIT_PATH ((str, pathlib.Path), optional): Path to project `__init__.py`. If None, then first
            found `__init__.py` is used. Defaults to None.

    Example:

        >>> import mypythontools
        >>> mypythontools.paths.set_paths()
        >>> mypythontools.paths.ROOT_PATH
        WindowsPath('...
        >>> mypythontools.paths.APP_PATH
        WindowsPath('...

    """
    global INIT_PATH
    global APP_PATH

    set_root(set_ROOT_PATH)

    INIT_PATH = find_path("__init__.py", ROOT_PATH) if not set_INIT_PATH else Path(set_INIT_PATH)
    APP_PATH = INIT_PATH.parent


def set_root(set_ROOT_PATH=None):
    """Set project root path and add it to sys.path if it's not already there.

    Args:
        set_ROOT_PATH ((str, pathlib.Path), optional): Path to project root where tests and docs folder are.
            If None, then cwd (current working directory) is used. Defaults to None.
    """
    global ROOT_PATH

    ROOT_PATH = Path(set_ROOT_PATH) if set_ROOT_PATH else Path.cwd()

    if not ROOT_PATH.as_posix() in sys.path:
        sys.path.insert(0, ROOT_PATH.as_posix())


def find_path(file, folder=None, exclude=["node_modules", "build", "dist"], levels=5):
    """Search for file in defined folder (cwd() by default) and return it's path.

    Args:
        file (str): Name with extension e.g. "app.py".
        folder (str, optional): Where to search. If None, then ROOT_PATH is used (cwd by default). Defaults to None.
        exclude (str, optional): List of folder names (anywhere in path) that will be ignored. Defaults to ['node_modules', 'build', 'dist'].
        levels (str, optional): Recursive number of analyzed folders. Defaults to 5.

    Returns:
        Path: Path of file.

    Raises:
        FileNotFoundError: If file is not found.
    """

    folder = ROOT_PATH if not folder else Path(folder).resolve()

    for lev in range(levels):
        glob_file_str = f"{'*/' * lev}{file}"

        for i in folder.glob(glob_file_str):
            isthatfile = True
            for j in exclude:
                if j in i.parts:
                    isthatfile = False
                    break
            if isthatfile:
                return i

    # If not returned - not found
    raise FileNotFoundError(mylogging.return_str(f"File `{file}` not found"))


def get_desktop_path():
    """Get desktop path.

    Returns:
        Path: Return pathlib Path object. If you want string, use `.as_posix()`
    """
    return Path.home() / "Desktop"
