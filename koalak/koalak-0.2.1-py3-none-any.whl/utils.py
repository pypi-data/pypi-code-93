import io
import os
import random
import shutil
import string
import sys
import tempfile
import types
from contextlib import contextmanager
from typing import Any, Dict, Iterable


@contextmanager
def tmp_module(
    module_name: str = None,
    context: Dict[str, Any] = None,
    addsys: bool = True,
    overwrite=False,
):
    """Generate a temporal module as context.
    Temporally add the module to sys.modules so it can be importable
    Args:
    """
    # TODO: unit test this function
    if not module_name:
        module_name = "tmpmodule_" + randomstr(exclude=list(sys.modules.keys()))
    else:
        if module_name in sys.modules and not overwrite:
            raise TabError("Module name already exist, call it with overwrite = True")

    context = context or {}
    module = types.ModuleType(module_name)
    module.__dict__.update(context)
    sys.modules[module_name] = module
    yield module
    del sys.modules[module_name]


@contextmanager
def temp_pathname():
    """Return an available pathname that you can use for files/dirs

    Will automatically clean the pathname if it's
    a file or directory"""
    tmpdir = tempfile.gettempdir()
    pathname = os.path.join(
        tmpdir, randomstr(20, prefix="tmppathname_", exclude=os.listdir(tmpdir))
    )
    try:
        yield pathname
    finally:
        if os.path.isdir(pathname):
            shutil.rmtree(pathname)
        elif os.path.isfile(pathname):
            os.remove(pathname)


def randomstr(
    n: int = 10,
    *,
    prefix="",
    alphabet: str = string.ascii_letters,
    exclude: Iterable = None
):
    """Generate random string of length n
    Args:
        n: length of returned string (without the prefix)
        alphabet: alphabet to use
        exclude: generated string must not be in this list (or any iterable object)
    """
    if exclude is not None:
        exclude = list(exclude)
    else:
        exclude = []

    while True:
        string = prefix + "".join(random.choices(alphabet, k=n))
        if string not in exclude:
            return string


@contextmanager
def temp_str2filename(string: str) -> str:
    """Generate a temporary file with the string content and
    return it's filename
    """
    with temp_pathname() as pathname:
        with open(pathname, "w") as f:
            f.write(string)
        yield pathname


@contextmanager
def str2stdin(string: str):
    string_io = io.StringIO(string)
    old_stdin = sys.stdin
    sys.stdin = string_io
    yield
    sys.stdin = old_stdin


@contextmanager
def file2stdin(filename: str):
    with open(filename) as f:
        old_stdin = sys.stdin
        sys.stdin = f
        try:
            yield
        # FIXME unit test finally with all other contextmanager
        finally:
            sys.stdin = old_stdin
