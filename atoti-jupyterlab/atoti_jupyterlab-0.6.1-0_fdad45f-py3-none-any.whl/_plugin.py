from pathlib import Path
from typing import Optional

from atoti._plugins import Plugin
from atoti.experimental.distributed.session import DistributedSession
from atoti.query.query_result import QueryResult
from atoti.query.session import QuerySession
from atoti.session import Session

from ._link import link
from ._visualize import visualize
from ._widget_conversion import create_query_result_repr_mimebundle_method_
from ._widget_manager import WidgetManager


class JupyterLabPlugin(Plugin):
    """JupyterLab plugin."""

    _widget_manager: WidgetManager = WidgetManager()

    def static_init(self):
        """Init to be called only once."""
        Session.link = link  # type: ignore
        DistributedSession.link = link  # type: ignore
        QuerySession.link = link  # type: ignore

        Session.visualize = visualize  # type: ignore
        DistributedSession.visualize = visualize  # type: ignore
        QuerySession.visualize = visualize  # type: ignore

        QueryResult._repr_mimebundle_ = create_query_result_repr_mimebundle_method_(
            original_method=QueryResult._repr_mimebundle_
        )

    def get_jar_path(self) -> Optional[Path]:
        """Return the path to the JAR."""
        return None

    def init_session(self, session: Session):
        """Initialize the session."""
        session._widget_manager = self._widget_manager  # type: ignore

    def init_query_session(self, query_session: QuerySession):
        """Initialize the query session."""
        query_session._widget_manager = self._widget_manager  # type: ignore
