# WARNING: This module may not import anything from within jupyhai
#          as it is being imported by `setup.py` – not all requirements
#          required are necessarily available during that import time.
import os
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from notebook.notebookapp import NotebookApp

__version__ = '1.2.2'


def _jupyter_server_extension_paths() -> List[dict]:
    return [{"module": "jupyhai"}]


def _jupyter_nbextension_paths() -> List[dict]:
    import pkg_resources

    jupyhai_js = pkg_resources.resource_filename('jupyhai', 'nbextension/jupyhai.js')
    if not os.path.isfile(jupyhai_js):
        raise RuntimeError(
            '%s is not a file – was the Jupyhai package built correctly?' % jupyhai_js
        )
    return [
        {
            'section': 'notebook',
            'src': jupyhai_js,
            'dest': 'jupyhai.js',
            'require': 'jupyhai',
        },
    ]


def load_jupyter_server_extension(nb_server_app: 'NotebookApp') -> None:
    from .handlers.init import prepare

    prepare(nb_server_app)
