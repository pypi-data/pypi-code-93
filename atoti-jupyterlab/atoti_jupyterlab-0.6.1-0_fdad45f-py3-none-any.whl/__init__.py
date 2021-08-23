"""Plugin to interactively visualize atoti sessions in JupyterLab.

This package is required to use :meth:`atoti.session.Session.visualize` and :meth:`atoti.query.session.QuerySession.visualize`.
"""

import json
from pathlib import Path
from typing import Collection, Mapping

_SOURCE_DIRECTORY = Path(__file__).parent

_LABEXTENSION_FOLDER = "labextension"

_PACKAGE_DATA = json.loads(
    (_SOURCE_DIRECTORY / _LABEXTENSION_FOLDER / "package.json").read_bytes()
)


def _jupyter_labextension_paths() -> Collection[Mapping[str, str]]:
    """Return the paths used by JupyterLab to load the extension assets."""
    return [{"src": _LABEXTENSION_FOLDER, "dest": _PACKAGE_DATA["name"]}]
