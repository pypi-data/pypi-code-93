from ._version import __version__
from .core import exec_sed_task, exec_sedml_docs_in_combine_archive  # noqa: F401
from .utils import get_boolnet

__all__ = [
    '__version__',
    'get_simulator_version',
    'exec_sed_task',
    'exec_sedml_docs_in_combine_archive',
]


def get_simulator_version():
    """ Get the version of BoolNet

    Returns:
        :obj:`str`: version
    """
    pkg = get_boolnet()
    return pkg.__version__
