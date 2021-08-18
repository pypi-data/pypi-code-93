from ._version import __version__
from .core import exec_sed_task, exec_sedml_docs_in_combine_archive  # noqa: F401
import re
import subprocess

__all__ = [
    '__version__',
    'get_simulator_version',
    'exec_sed_task',
    'exec_sedml_docs_in_combine_archive',
]


def get_simulator_version():
    """ Get the installed version of XPP

    Returns:
        :obj:`str`: version
    """
    result = subprocess.run(["xppaut", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode != 0:
        raise RuntimeError('XPP failed: {}'.format(result.stdout.decode("utf-8")))
    return re.search(r"(\d+\.\d*|\d*\.\d+)", result.stdout.decode("utf-8")).group(0)
