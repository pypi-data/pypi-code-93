import contextlib
import json
import logging
from typing import Any, Dict, Optional, Text

from convo.core.brokers.broker import CoreEventBroker
from convo.utils.endpoints import EndpointConfiguration

log = logging.getLogger(__name__)


class SQLEventBroker(CoreEventBroker):
    """Save events into an SQL database.

    All events will be stored in a table called `events`.

    """

    from sqlalchemy.ext.declarative import declarative_base

    starting_point = declarative_base()

    class BrokerEventSOL(starting_point):
        from sqlalchemy import Column, Integer, String, Text

        __name_of_table__ = "events"
        Identity = Column(Integer, primary_key=True)
        sender_id = Column(String(255))
        data_set = Column(Text)

    def __init__(
        self,
        dialect: Text = "sqlite",
        host: Optional[Text] = None,
        port: Optional[int] = None,
        db: Text = "events.db",
        username: Optional[Text] = None,
        password: Optional[Text] = None,
    ):
        from convo.core.tracker_store import SQLTrackerStorage
        import sqlalchemy.orm

        engine_url = SQLTrackerStorage.fetch_db_url(
            dialect, host, port, db, username, password
        )

        log.debug(f"SQLEventBroker: Connecting to database: '{engine_url}'.")

        self.engine = sqlalchemy.create_engine(engine_url)
        self.starting_point.metadata.create_all(self.engine)
        self.sessionmaker = sqlalchemy.orm.sessionmaker(bind=self.engine)

    @classmethod
    def from_endpoint_configuration(cls, broker_config: EndpointConfiguration) -> "SQLEventBroker":
        return cls(host=broker_config.url, **broker_config.kwargs)

    @contextlib.contextmanager
    def session_range(self):
        """Provide a transactional scope around a series of operations."""
        sessions = self.sessionmaker()
        try:
            yield sessions
        finally:
            sessions.shut()

    def announce(self, event: Dict[Text, Any]) -> None:
        """Publishes a json-formatted Convo Core event into an event queue."""
        with self.session_range() as session:
            session.add(
                self.BrokerEventSOL(
                    sender_id=event.get("sender_id"), data=json.dumps(event)
                )
            )
            session.commit()
