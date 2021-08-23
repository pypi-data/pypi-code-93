from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Union

from typing_extensions import TypedDict

from atoti.experimental.distributed.session import DistributedSession
from atoti.query.session import QuerySession
from atoti.session import Session

from ._mime_types import LINK_MIME_TYPE

_Session = Union[Session, DistributedSession, QuerySession]


class LocalSessionLocation(TypedDict):
    https: bool
    port: int


class QuerySessionLocation(TypedDict):
    url: str


def get_session_location(
    session: _Session,
) -> Union[LocalSessionLocation, QuerySessionLocation]:
    return (
        QuerySessionLocation(url=session.url.rstrip("/"))
        if isinstance(session, QuerySession)
        else LocalSessionLocation(
            https=session._config.https is not None, port=session.port
        )
    )


@dataclass(frozen=True)
class Link:
    _path: str
    _session: _Session

    def _repr_mimebundle_(
        self, include: Any, exclude: Any  # pylint: disable=unused-argument
    ) -> Mapping[str, Any]:
        return {
            "text/plain": """Open the notebook in JupyterLab with the atoti extension enabled to see this link.""",
            LINK_MIME_TYPE: {
                "path": self._path,
                "sessionLocation": get_session_location(self._session),
            },
        }


def link(session: _Session, *, path: str = "") -> Any:
    """Display a link to this session.

    Clicking on the link will open it in a new browser tab.

    Note:
        This method requires the :mod:`atoti-jupyterlab <atoti_jupyterlab>` plugin.

    The extension will try to access the session through (in that order):

    #. `Jupyter Server Proxy <https://jupyter-server-proxy.readthedocs.io/>`__ if it is enabled.
    #. ``f"{session_protocol}//{jupyter_server_hostname}:{session.port}"`` for :class:`~atoti.session.Session` and ``session.url`` for :class:`~atoti.query.session.QuerySession`.

    Args:
        path: The path to append to the session base URL.
            Defaults to the session home page.

    Example:

        Pointing directly to an existing dashboard:

        .. testcode::

            dashboard_id = "92i"
            session.link(path=f"#/dashboard/{dashboard_id}")

    """
    return Link(path.lstrip("/"), session)
