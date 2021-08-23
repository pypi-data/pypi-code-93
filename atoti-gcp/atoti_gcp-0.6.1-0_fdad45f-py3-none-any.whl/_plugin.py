from pathlib import Path
from typing import Optional

from atoti._plugins import Plugin
from atoti.query.session import QuerySession
from atoti.session import Session

JAR_PATH = (Path(__file__).parent / "data" / "atoti-gcp.jar").absolute()


class GCPPlugin(Plugin):
    """GCP plugin."""

    def static_init(self):
        """Init to be called only once."""

    def get_jar_path(self) -> Optional[Path]:
        """Return the path to the JAR."""
        return JAR_PATH

    def init_session(self, session: Session):
        """Initialize the session."""
        session._java_api.gateway.jvm.io.atoti.loading.gcp.GcpPlugin.init()  # type: ignore

    def init_query_session(self, query_session: QuerySession):
        """Initialize the query session."""
