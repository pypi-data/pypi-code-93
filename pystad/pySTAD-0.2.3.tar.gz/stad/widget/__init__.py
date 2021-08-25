"""
A module containing a jupyter-lab widget to interactively visualize networks.

Classes
-------
Widget :
  The jupyter-lab widget.

Functions
---------
_jupyter_labextension_paths :
  Implementation detail of jupyter-lab widgets
"""
from .widget import *

def _jupyter_labextension_paths():
    """Called by Jupyter Lab Server to detect if it is a valid labextension and
    to install the widget

    Returns
    =======
    src: Source directory name to copy files from. Webpack outputs generated files
        into this directory and Jupyter Lab copies from this directory during
        widget installation
    dest: Destination directory name to install widget files to. Jupyter Lab copies
        from `src` directory into <jupyter path>/labextensions/<dest> directory
        during widget installation
    """
    return [{
        'src': 'labextension',
        'dest': 'jupyter_stad',
    }]
