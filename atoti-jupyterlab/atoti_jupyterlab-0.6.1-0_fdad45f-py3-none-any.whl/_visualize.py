from __future__ import annotations

from typing import Any, Optional

from atoti._base._base_session import BaseSession


def visualize(self: BaseSession[Any], name: Optional[str] = None):  # noqa: D417
    """Display an atoti widget to explore the session interactively.

    Note:
        This method requires the :mod:`atoti-jupyterlab <atoti_jupyterlab>` plugin.

    The widget state will be stored in the cell metadata.
    This state should not have to be edited but, if desired, it can be found in JupyterLab by opening the "Notebook tools" sidebar and expanding the the "Advanced Tools" section.

    Args:
        name: The name to give to the widget.
    """
    self._widget_manager.display_widget(self, name)  # type: ignore
