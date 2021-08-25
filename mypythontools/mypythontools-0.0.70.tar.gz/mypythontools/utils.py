"""
This module can be used for example in running deploy pipelines or githooks
(some code automatically executed before commit). This module can run the tests,
edit library version, generate rst files for docs, push to git or deploy app to pypi.

All of that can be done with one function call - with `push_pipeline` function that
run other functions, or you can use functions separately. If you are using other
function than `push_pipeline`, you need to call `mypythontools.paths.set_paths()` first.


Examples:
=========

    **VS Code Task example**

    You can push changes with single click with all the hooks displaying results in
    your terminal. All params changing every push (like git message or tag) can
    be configured on the beginning and therefore you don't need to wait for test finish.
    Default values can be also used, so in small starting projects, push is actually very fast.

    Create folder utils, create `push_script.py` inside, add

    >>> import mypythontools
    ...
    >>> if __name__ == "__main__":
    ...     # Params that are always the same define here. Params that are changing define in IDE when run action.
    ...     # For example in tasks (command line arguments and argparse will be used).
    ...     mypythontools.utils.push_pipeline(deploy=True)

    Then just add this task to global tasks.json::

        {
        "version": "2.0.0",
        "tasks": [
            {
            "label": "Build app",
            "type": "shell",
            "command": "python",
            "args": ["${workspaceFolder}/utils/build_script.py"],
            "presentation": {
                "reveal": "always",
                "panel": "new"
            }
            },
            {
            "label": "Hooks & push & deploy",
            "type": "shell",
            "command": "python",
            "args": [
                "${workspaceFolder}/utils/push_script.py",
                "--version",
                "${input:version}",
                "--commit_message",
                "${input:commit_message}",
                "--tag",
                "${input:tag}",
                "--tag_mesage",
                "${input:tag-message}"
            ],
            "presentation": {
                "reveal": "always",
                "panel": "new"
            }
            }
        ],
        "inputs": [
            {
            "type": "promptString",
            "id": "version",
            "description": "Version in __init__.py will be overwiten. Version has to be in format like '1.0.3' three digits and two dots. If None, nothing will happen. If 'increment', than it will be updated by 0.0.1.",
            "default": "increment"
            },
            {
            "type": "promptString",
            "id": "commit_message",
            "description": "Git message for commit.",
            "default": "New commit"
            },
            {
            "type": "promptString",
            "id": "tag",
            "description": "Git tag. If '__version__' is used, then tag from version in __init__.py will be derived. E.g. 'v1.0.1' from '1.0.1'",
            "default": "__version__"
            },
            {
            "type": "promptString",
            "id": "tag-message",
            "description": "Git tag message.",
            "default": "New version"
            }
        ]
        }

    **Git hooks example**

    Create folder git_hooks with git hook file - for prec commit name must be `pre-commit`
    (with no extension). Hooks in git folder are gitignored by default (and hooks is not visible
    on first sight).

    Then add hook to git settings - run in terminal (last arg is path (created folder))::

        $ git config core.hooksPath git_hooks

    In created folder on first two lines copy this::

        #!/usr/bin/env python
        # -*- coding: UTF-8 -*-

    Then just import any function from here and call with desired params. E.g.

    >>> import mypythontools
    >>> mypythontools.paths.set_paths()
    >>> version = mypythontools.utils.get_version()  # For example 1.0.2
    >>> print(version[0].isdigit() == version[2].isdigit() == version[5].isdigit() == (version[1] == '.' == version[3]))
    True
"""

import argparse
import ast
import importlib
from pathlib import Path
import subprocess
import sys

import mylogging

from . import paths
from . import tests
from . import deploy as deploy_module

# Lazy loaded
# from git import Repo


def push_pipeline(
    test=True,
    test_options={},
    version="increment",
    sphinx_docs=True,
    push_git=True,
    commit_message="New commit",
    tag="__version__",
    tag_mesage="New version",
    deploy=False,
):
    """Run pipeline for pushing and deploying app. Can run tests, generate rst files for sphinx docs,
    push to github and deploy to pypi. All params can be configured not only with function params,
    but also from command line with params and therefore callable from terminal and optimal to run
    from IDE (for example with creating simple VS Code task).

    Check utils module docs for implementation example.

    Args:
        test (bool, optional): Whether run pytest tests. Defaults to True.
        test_options (dict, optional): Parameters of tests function e.g. `{"test_coverage": True, "verbose": False, "use_virutalenv":True}`.
            Defaults to {}.
        version (str, optional): New version. E.g. '1.2.5'. If 'increment', than it's auto incremented. E.g from '1.0.2' to 'v1.0.3'.
            If None, then version is not changed. 'Defaults to "increment".
        sphinx_docs((bool, list), optional): Whether generate sphinx apidoc and generate rst files for documentation.
            Some files in docs source can be deleted - check `sphinx_docs` docstrings for details and insert
            `exclude_paths` list if have some extra files other than ['conf.py', 'index.rst', '_static', '_templates'].
            Defaults to True.
        push_git (bool, optional): Whether push repository on git with git_message, tag and tag message. Defaults to True.
        git_message (str, optional): Git message. Defaults to 'New commit'.
        tag (str, optional): Used tag. If None, not tag will be pushed. If tag is '__version__', than updated version from __init__ is used.
            Defaults to __version__.
        tag_mesage (str, optional): Tag message. Defaults to New version.
        deploy (bool, optional): Whether deploy to PYPI. Defaults to False.

    Example:
        Recommended use is from IDE (for example with Tasks in VS Code). Check utils docs for how to use it.
        You can also use it from python...

        >>> import mypythontools
        ...
        >>> if __name__ == "__main__":
        ...     mypythontools.utils.push_pipeline(deploy=True)  # All the params that change everytime configure for example in VS Code tasks.

    """
    config = {
        "test": test,
        "test_options": test_options,
        "version": version,
        "sphinx_docs": sphinx_docs,
        "push_git": push_git,
        "commit_message": commit_message,
        "tag": tag,
        "tag_mesage": tag_mesage,
        "deploy": deploy,
    }

    if not all([paths.ROOT_PATH, paths.APP_PATH, paths.INIT_PATH]):
        paths.set_paths()

    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="Prediction framework setting via command line parser!")

        parser.add_argument(
            "--version",
            type=str,
            help=(
                "Version in __init__.py will be overwiten. Version has to be in format like '1.0.3' three digits"
                "and two dots. If None, nothing will happen. If 'increment', than it will be updated by 0.0.1."
            ),
        )
        parser.add_argument(
            "--commit_message",
            type=str,
            help="Commit message. Defaults to: 'New commit'",
        )
        parser.add_argument(
            "--tag",
            type=str,
            help="Tag. E.g 'v1.1.2'. If '__version__', get the version. Defaults to: '__version__'",
        )
        parser.add_argument("--tag_mesage", type=str, help="Tag message. Defaults to: 'New version'")

        parser_args_dict = {k: v for k, v in parser.parse_known_args()[0].__dict__.items() if v is not None}

        if parser_args_dict:
            config.update(parser_args_dict)

    if config["test"]:
        tests.run_tests(**test_options)

    if config["version"]:
        set_version(config["version"])

    if isinstance(config["sphinx_docs"], list):
        sphinx_docs_regenerate(exclude_paths=config["sphinx_docs"])
    elif config["sphinx_docs"]:
        sphinx_docs_regenerate()

    if push_git:
        git_push(
            commit_message=config["commit_message"],
            tag=config["tag"],
            tag_message=config["tag_mesage"],
        )

    if config["deploy"]:
        deploy_module.deploy_to_pypi()


def git_push(commit_message, tag="__version__", tag_message="New version"):
    """Stage all changes, commit, add tag and push. If tag = '__version__', than tag
    is infered from __init__.py.

    Args:
        commit_message (str): Commit message.
        tag (str, optional): Define tag used in push. If tag is '__version__', than is automatically generated
            from __init__ version. E.g from '1.0.2' to 'v1.0.2'.  Defaults to '__version__'.
        tag_message (str, optional): Message in anotated tag. Defaults to 'New version'.
    """

    from git import Repo

    git_add_command = "git add . "

    subprocess.run(git_add_command.split(), shell=True, check=True, cwd=paths.ROOT_PATH)

    subprocess.run(
        ["git", "commit", "-m", commit_message],
        shell=True,
        check=True,
        cwd=paths.ROOT_PATH,
    )

    if not tag_message:
        tag_message = "New version"

    if tag == "__version__":
        tag = f"v{get_version()}"

    git_push_command = "git push"

    if tag:
        Repo(paths.ROOT_PATH).create_tag(tag, message=tag_message)
        git_push_command += " --follow-tags"

    subprocess.run(git_push_command, shell=True, check=True, cwd=paths.ROOT_PATH)


def set_version(version="increment"):
    """Change your version in your __init__.py file.


    Args:
        version (str, optional): If version is 'increment', it will increment your __version__
            in you __init__.py by 0.0.1. Defaults to "increment".

    Raises:
        ValueError: If no __version__ is find. Try set INIT_PATH via paths.set_paths...
    """

    if version == "increment" or (
        len(version) == 5
        and version[1] == version[3] == "."
        and (version[0].isdigit() and version[2].isdigit() and version[4].isdigit())
    ):
        pass
    else:
        raise ValueError(
            mylogging.return_str(
                f"Version not validated. Version has to be of form '1.2.3'. Three digits and two dots. You used {version}"
            )
        )

    with open(paths.INIT_PATH, "r") as init_file:

        list_of_lines = init_file.readlines()

        for i, j in enumerate(list_of_lines):
            if j.startswith("__version__"):

                found = True

                delimiter = '"' if '"' in j else "'"
                delimited = j.split(delimiter)

                if version == "increment":
                    version_list = delimited[1].split(".")
                    version_list[2] = str(int(version_list[2]) + 1)
                    delimited[1] = ".".join(version_list)

                else:
                    delimited[1] = version

                list_of_lines[i] = delimiter.join(delimited)
                break

        if not found:
            raise ValueError(
                mylogging.return_str("__version__ variable not found in __init__.py. Try set INIT_PATH.")
            )

    with open(paths.INIT_PATH, "w") as init_file:

        init_file.writelines(list_of_lines)


def get_version(INIT_PATH=None):
    """Get version info from __init__.py file.

    Args:
        INIT_PATH ((str, Path), optional): Path to __init__.py file. If None, it's taken from paths module
            if used paths.set_paths() before. Defaults to None.

    Returns:
        str: String of version from __init__.py.

    Raises:
        ValueError: If no __version__ is find. Try set INIT_PATH...
    """

    if not INIT_PATH:
        INIT_PATH = paths.INIT_PATH

    with open(INIT_PATH, "r") as init_file:

        for line in init_file:

            if line.startswith("__version__"):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]

        else:
            raise ValueError(
                mylogging.return_str("__version__ variable not found in __init__.py. Try set INIT_PATH.")
            )


def sphinx_docs_regenerate(
    docs_path=None, build_locally=False, git_add=True, exclude_paths=[], delete=["modules.rst"]
):
    """This will generate all rst files necessary for sphinx documentation generation with sphinx-apidoc.
    It automatically delete removed and renamed files.

    Note:
        All the files except ['conf.py', 'index.rst', '_static', '_templates'] will be deleted!!!
        Because if some files would be deleted or renamed, rst would stay and html was generated.
        If you have some extra files or folders in docs source - add it to `exclude_paths` list.

    Function suppose sphinx build and source in separate folders...

    Args:
        docs_path ((str, Path), optional): Where source folder is. Usually infered automatically.
            Defaults to None.
        build_locally (bool, optional): If true, build folder with html files locally.
            Defaults to False.
        git_add (bool, optional): Whether to add generated files to stage. False mostly for
            testing reasons. Defaults to True.
        exclude_paths (list, optional): List of files and folder names that will not be deleted.
            ['conf.py', 'index.rst', '_static', '_templates'] are excluded by default. Defaults to [].
        delete (list, optional): If delete some files (for example to have no errors in sphinx build for unused modules)

    Note:
        Function suppose structure of docs like::

            -- docs
            -- -- source
            -- -- -- conf.py
            -- -- make.bat

        If you are issuing error, try set project root path with `set_root`
    """

    if not importlib.util.find_spec("sphinx"):
        raise ImportError(
            mylogging.return_str(
                "Sphinx library is necessary for docs generation. Install via `pip install sphinx`"
            )
        )

    if not docs_path:
        if paths.ROOT_PATH:
            docs_path = paths.ROOT_PATH / "docs"
        else:
            raise NotADirectoryError(
                mylogging.return_str(
                    "`docs_path` not found. Setup it with parameter `docs_path` or use `paths.set_paths()` function."
                )
            )

    if not all([paths.APP_PATH, paths.ROOT_PATH]):
        mylogging.return_str("Paths are not known. First run `paths.set_paths()`.")

    docs_source_path = Path(docs_path).resolve() / "source"

    for p in docs_source_path.iterdir():
        if p.name not in [
            "conf.py",
            "index.rst",
            "_static",
            "_templates",
            *exclude_paths,
        ]:
            try:
                p.unlink()
            except Exception:
                pass

    apidoc_command = f"sphinx-apidoc -f -e -o source {paths.APP_PATH.as_posix()}"
    subprocess.run(
        apidoc_command,
        shell=True,
        cwd=docs_path,
        check=True,
    )

    if delete:
        for i in delete:
            (docs_source_path / i).unlink()

    if build_locally:
        subprocess.run(["make", "html"], shell=True, cwd=docs_path, check=True)

    if git_add:
        subprocess.run(["git", "add", "docs"], shell=True, cwd=paths.ROOT_PATH, check=True)


def generate_readme_from_init(git_add=True):
    """Because i had very similar things in main __init__.py and in readme. It was to maintain news
    in code. For better simplicity i prefer write docs once and then generate. One code, two use cases.

    Why __init__? - Because in IDE on mouseover developers can see help.
    Why README.md? - Good for github.com

    If issuing problems, try paths.set_root() to library path.

    Args:
        git_add (bool, optional): Whether to add generated files to stage. False mostly
            for testing reasons. Defaults to True.
    """

    with open(paths.INIT_PATH) as fd:
        file_contents = fd.read()
    module = ast.parse(file_contents)
    docstrings = ast.get_docstring(module)

    if docstrings is None:
        docstrings = ""

    with open(paths.ROOT_PATH / "README.md", "w") as file:
        file.write(docstrings)

    if git_add:
        subprocess.run(["git", "add", "README.md"], shell=True, cwd=paths.ROOT_PATH, check=True)
