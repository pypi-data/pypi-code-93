import contextlib
import itertools
import json
import logging
import os
import pickle
from datetime import datetime, timezone

from time import sleep
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Text,
    Union,
    TYPE_CHECKING,
)

from boto3.dynamodb.conditions import Key
import convo.core.utils as core_utils
import convo.shared.utils.cli
import convo.shared.utils.common
import convo.shared.utils.io
from convo.shared.core.constants import LISTEN_ACTION_NAME  
from convo.core.brokers.broker import CoreEventBroker
from convo.core.constants import (
    POSTGRESQL_SCHEMA_NAME,
    POSTGRESQL_MAXIMUM_OVERFLOW,
    POSTGRESQL_POOL_SIZE,
)
from convo.shared.core.conversation import Dialogue
from convo.shared.core.domain import Domain
from convo.shared.core.events import SessionBegan
from convo.shared.core.trackers import (
    ActionExecuted,
    DialogueStateTracer,
    releaseVerbosity,
)
import convo.cli.utils as convo_cli_utils
from convo.shared.nlu.constants import KEY_INTENT_NAME
from convo.utils import common as common_utils
from convo.utils.endpoints import EndpointConfiguration
import sqlalchemy as sa

if TYPE_CHECKING:
    import boto3.resources.factory.dynamodb.Table
    from sqlalchemy.engine.url import URL
    from sqlalchemy.engine.base import Engine
    from sqlalchemy.orm.session import Session
    from sqlalchemy import Sequence
    from sqlalchemy.orm.query import Query

log = logging.getLogger(__name__)

# default values of PostgreSQL pool size and max overflow
POSTGRESQL_BY_DEFAULT_MAXIMUM_OVERFLOW = 100
POSTGRESQL_BY_DEFAULT_POOL_SIZE = 50


class TrackerStorage:
    """Class to hold all of the TrackerStorage classes"""

    def __init__(
        self,
        domain: Optional[Domain],
        event_broker: Optional[CoreEventBroker] = None,
        retrieve_events_from_previous_conversation_sessions: bool = False,
    ) -> None:
        """Create a TrackerStorage.

        Args:
            domain: The `Domain` to initialize the `DialogueStateTracer`.
            event_broker: An event broker to publish any new events to another
                destination.
            retrieve_events_from_previous_conversation_sessions: If `True`, `retrieve`
                will return all events (even if they are from a previous conversation
                session). This setting only applies to `TrackerStorage`s which usually
                would only return events for the latest session.
        """
        self.domain = domain
        self.event_broker = event_broker
        self.max_event_history = None
        self.load_events_from_previous_conversation_sessions = (
            retrieve_events_from_previous_conversation_sessions
        )

    @staticmethod
    def create(
        obj: Union["TrackerStorage", EndpointConfiguration, None],
        domain: Optional[Domain] = None,
        event_broker: Optional[CoreEventBroker] = None,
    ) -> "TrackerStorage":
        """Factory to create a tracker store."""

        if isinstance(obj, TrackerStorage):
            return obj
        else:
            return _generate_from_endpoint_configuration(obj, domain, event_broker)

    def fetch_or_generate_tracker(
        self,
        sender_id: Text,
        max_event_history: Optional[int] = None,
        append_action_listen: bool = True,
    ) -> "DialogueStateTracer":
        """Returns tracker or creates one if the retrieval returns None.

        Args:
            sender_id: Conversation ID associated with the requested tracker.
            max_event_history: Value to update the tracker store's max event history to.
            append_action_listen: Whether or not to append an initial `action_listen`.
        """
        tracer = self.recover(sender_id)
        self.max_event_history = max_event_history
        if tracer is None:
            tracer = self.generate_tracker(
                sender_id, append_action_listen=append_action_listen
            )
        return tracer

    def init_tracer(self, sender_id: Text) -> "DialogueStateTracer":
        """Returns a Dialogue fetch_state Tracker"""
        return DialogueStateTracer(
            sender_id,
            self.domain.slots if self.domain else None,
            max_event_history=self.max_event_history,
        )

    def generate_tracker(
        self, sender_id: Text, append_action_listen: bool = True
    ) -> DialogueStateTracer:
        """Creates a new tracker for `sender_id`.

        The tracker begins with a `SessionBegan` event and is initially listening.

        Args:
            sender_id: Conversation ID associated with the tracker.
            append_action_listen: Whether or not to append an initial `action_listen`.

        Returns:
            The newly created tracker for `sender_id`.

        """

        tracker = self.init_tracer(sender_id)

        if tracker:
            if append_action_listen:
                tracker.update(ActionExecuted(LISTEN_ACTION_NAME  ))

            self.save(tracker)

        return tracker

    def save(self, tracker):
        """Save method that will be overridden by specific tracker"""
        raise NotImplementedError()

    def recover(self, sender_id: Text) -> Optional[DialogueStateTracer]:
        """Retrieve method that will be overridden by specific tracker"""
        raise NotImplementedError()

    def fetch_stream_events(self, tracker: DialogueStateTracer) -> None:
        """Streams events to a message broker"""
        off_set = self.no_of_existing_events(tracker.sender_id)
        fetch_events = tracker.events
        for event in list(itertools.islice(fetch_events, off_set, len(fetch_events))):
            matter = {"sender_id": tracker.sender_id}
            matter.update(event.as_dictionary())
            self.event_broker.publish(matter)

    def no_of_existing_events(self, sender_id: Text) -> int:
        """Return number of stored events for a given sender id."""
        tracker_old = self.recover(sender_id)
        return len(tracker_old.events) if tracker_old else 0

    def keys(self) -> Iterable[Text]:
        """Returns the set of values for the tracker store's primary key"""
        raise NotImplementedError()

    @staticmethod
    def serialise_tracker_data(tracker: DialogueStateTracer) -> Text:
        """Serializes the tracker, returns representation of the tracker."""
        conversation = tracker.asDialogue()

        return json.dumps(conversation.as_dictionary())

    @staticmethod
    def _deserialise_chat_from_pickle(
        sender_id: Text, serialised_tracker: bytes
    ) -> Dialogue:

        convo.shared.utils.io.rasing_deprecate_warning(
            f"Found pickled tracker for "
            f"conversation ID '{sender_id}'. Deserialisation of pickled "
            f"trackers is deprecated. Convo will perform any "
            f"future save operations of this tracker using json serialisation."
        )
        return pickle.loads(serialised_tracker)

    def deserialise_tracker_data(
        self, sender_id: Text, serialised_tracker: Union[Text, bytes]
    ) -> Optional[DialogueStateTracer]:
        """Deserializes the tracker and returns it."""

        tracer = self.init_tracer(sender_id)
        if not tracer:
            return None

        try:
            conversation = Dialogue.from_params(json.loads(serialised_tracker))
        except UnicodeDecodeError:
            conversation = self._deserialise_chat_from_pickle(
                sender_id, serialised_tracker
            )

        tracer.recreate_from_dialogue(conversation)

        return tracer


class InMemoryTrackerStorage(TrackerStorage):
    """Stores conversation history in memory"""

    def __init__(
        self, domain: Domain, event_broker: Optional[CoreEventBroker] = None
    ) -> None:
        self.store = {}
        super().__init__(domain, event_broker)

    def save(self, tracker: DialogueStateTracer) -> None:
        """Updates and saves the current conversation state"""
        if self.event_broker:
            self.fetch_stream_events(tracker)
        serialised_data = InMemoryTrackerStorage.serialise_tracker_data(tracker)
        self.store[tracker.sender_id] = serialised_data

    def recover(self, sender_id: Text) -> Optional[DialogueStateTracer]:
        """
        Args:
            sender_id: the message owner ID

        Returns:
            DialogueStateTracer
        """
        if sender_id in self.store:
            log.debug(f"Recreating tracker for id '{sender_id}'")
            return self.deserialise_tracker_data(sender_id, self.store[sender_id])
        else:
            log.debug(f"Creating a new tracker for id '{sender_id}'.")
            return None

    def keys(self) -> Iterable[Text]:
        """Returns sender_ids of the Tracker Store in memory"""
        return self.store.keys()


class RedisTrackerStorage(TrackerStorage):
    """Stores conversation history in Redis"""

    def __init__(
        self,
        domain,
        host="localhost",
        port=6379,
        db=0,
        password: Optional[Text] = None,
        event_broker: Optional[CoreEventBroker] = None,
        record_exp: Optional[float] = None,
        use_ssl: bool = False,
    ):
        import redis

        self.red = redis.StrictRedis(
            host=host, port=port, db=db, password=password, ssl=use_ssl
        )
        self.record_exp = record_exp
        super().__init__(domain, event_broker)

    def save(self, tracker, time_over=None):
        """Saves the current conversation state"""
        if self.event_broker:
            self.fetch_stream_events(tracker)

        if not time_over and self.record_exp:
            time_over = self.record_exp

        serialised_tracker_data = self.serialise_tracker_data(tracker)
        self.red.set(tracker.sender_id, serialised_tracker_data, ex=time_over)

    def recover(self, sender_id):
        """
        Args:
            sender_id: the message owner ID

        Returns:
            DialogueStateTracer
        """
        stored_data = self.red.get(sender_id)
        if stored_data is not None:
            return self.deserialise_tracker_data(sender_id, stored_data)
        else:
            return None

    def keys(self) -> Iterable[Text]:
        """Returns keys of the Redis Tracker Store"""
        return self.red.keys()


class DynamoTrackerStorage(TrackerStorage):
    """Stores conversation history in DynamoDB"""

    def __init__(
        self,
        domain: Domain,
        table_name: Text = "states",
        region: Text = "us-east-1",
        event_broker: Optional[EndpointConfiguration] = None,
    ):
        """Initialize `DynamoTrackerStore`.

        Args:
            domain: Domain associated with this tracker store.
            table_name: The name of the DynamoDB table, does not need to be present a
                priori.
            region: The name of the region associated with the client.
                A client is associated with a single region.
            event_broker: An event broker used to publish events.
        """
        import boto3

        self.client = boto3.client("dynamodb", region_name=region)
        self.region = region
        self.table_name = table_name
        self.db = self.get_or_create_table(table_name)
        super().__init__(domain, event_broker)

    def get_or_create_table(
        self, table_name: Text
    ) -> "boto3.resources.factory.dynamodb.Table":
        """Returns table or creates one if the table name is not in the table list"""
        import boto3

        dynamo_generator = boto3.resource("dynamodb", region_name=self.region)
        try:
            self.client.describe_table(TableName=table_name)
        except self.client.exceptions.ResourceNotFoundException:
            data_table = dynamo_generator.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {"AttributeName": "sender_id", "KeyType": "HASH"},
                    {"AttributeName": "session_date", "KeyType": "RANGE"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "sender_id", "AttributeType": "S"},
                    {"AttributeName": "session_date", "AttributeType": "N"},
                ],
                ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            )

            # Wait until the table exists.
            data_table.meta.client.get_waiter("table_exists").wait(TableName=table_name)
        return dynamo_generator.Table(table_name)

    def save(self, tracker):
        """Saves the current conversation state"""
        if self.event_broker:
            self.fetch_stream_events(tracker)
        self.db.put_item(Item=self.serialise_tracker_data(tracker))

    def serialise_tracker_data(self, tracker: "DialogueStateTracer") -> Dict:
        """Serializes the tracker, returns object with decimal types"""
        e = tracker.asDialogue().as_dictionary()
        e.update(
            {
                "sender_id": tracker.sender_id,
                "session_date": int(datetime.now(tz=timezone.utc).timestamp()),
            }
        )
        # DynamoDB cannot store `float`s, so we'll convert them to `Decimal`s
        return core_utils.change_floats_with_decimals_values(e)

    def recover(self, sender_id: Text) -> Optional[DialogueStateTracer]:
        """Create a tracker from all previously stored events."""
        # Retrieve dialogues for a sender_id in reverse-chronological order based on
        # the session_date sort key
        conversations = self.db.query(
            KeyConditionExpression=Key("sender_id").eq(sender_id),
            Limit=1,
            ScanIndexForward=False,
        )["Items"]

        if not conversations:
            return None

        events = conversations[0].get("events", [])

        # `float`s are stored as `Decimal` objects - we need to convert them back
        events_with_float_type = core_utils.replace_decimals_with_floats(events)

        return DialogueStateTracer.from_dict(
            sender_id, events_with_float_type, self.domain.slots
        )

    def keys(self) -> Iterable[Text]:
        """Returns sender_ids of the DynamoTrackerStore"""
        return [
            i["sender_id"]
            for i in self.db.scan(ProjectionExpression="sender_id")["Items"]
        ]


class MongoTrackerStorage(TrackerStorage):
    """
    Stores conversation history in Mongo

    Property methods:
        conversations: returns the current conversation
    """

    def __init__(
        self,
        domain: Domain,
        host: Optional[Text] = "mongodb://localhost:27017",
        db: Optional[Text] = "convo",
        username: Optional[Text] = None,
        password: Optional[Text] = None,
        auth_source: Optional[Text] = "admin",
        collection: Optional[Text] = "conversations",
        event_broker: Optional[CoreEventBroker] = None,
    ):
        from pymongo.database import Database
        from pymongo import MongoClient

        self.client = MongoClient(
            host,
            username=username,
            password=password,
            authSource=auth_source,
            # delay connect until process forking is done
            connect=False,
        )

        self.db = Database(self.client, db)
        self.collection = collection
        super().__init__(domain, event_broker)

        self._ensure_index()

    @property
    def chat(self):
        """Returns the current conversation"""
        return self.db[self.collection]

    def _ensure_index(self):
        """Create an index on the sender_id"""
        self.chat.create_index("sender_id")

    @staticmethod
    def _present_tracker_state_without_events(tracker: DialogueStateTracer) -> Dict:
        # get current tracker state and remove `events` key from state
        # since events are pushed separately in the `update_one()` operation
        tracker_store_state = tracker.current_active_state(releaseVerbosity.ALL)
        tracker_store_state.pop("events", None)

        return tracker_store_state

    def save(self, tracker, timeout=None):
        """Saves the current conversation state"""
        if self.event_broker:
            self.fetch_stream_events(tracker)

        extra_events = self._extra_events(tracker)

        self.chat.update_one(
            {"sender_id": tracker.sender_id},
            {
                "$set": self._present_tracker_state_without_events(tracker),
                "$push": {
                    "events": {"$each": [e.as_dictionary() for e in extra_events]}
                },
            },
            upsert=True,
        )

    def _extra_events(self, tracker: DialogueStateTracer) -> Iterator:
        """Return events from the tracker which aren't currently stored.

        Args:
            tracker: Tracker to inspect.

        Returns:
            List of serialised events that aren't currently stored.

        """

        stored_data = self.chat.find_one({"sender_id": tracker.sender_id}) or {}
        every_events = self._events_from_serialized_tracker_data(stored_data)
        no_events_since_last_session = len(
            self._events_since_last_session_begins(every_events)
        )

        return itertools.islice(
            tracker.events, no_events_since_last_session, len(tracker.events)
        )

    @staticmethod
    def _events_from_serialized_tracker_data(serialised: Dict) -> List[Dict]:
        return serialised.get("events", [])

    @staticmethod
    def _events_since_last_session_begins(events: List[Dict]) -> List[Dict]:
        """Retrieve events since and including the latest `SessionStart` event.

        Args:
            events: All events for a conversation ID.

        Returns:
            List of serialised events since and including the latest `SessionBegan`
            event. Returns all events if no such event is found.

        """

        events_after_session_begins = []
        for event in reversed(events):
            events_after_session_begins.append(event)
            if event["event"] == SessionBegan.type_name:
                break

        return list(reversed(events_after_session_begins))

    def recover(self, sender_id: Text) -> Optional[DialogueStateTracer]:
        """
        Args:
            sender_id: the message owner ID

        Returns:
            `DialogueStateTracer`
        """
        stored_data = self.chat.find_one({"sender_id": sender_id})

        # look for conversations which have used an `int` sender_id in the past
        # and update them.
        if not stored_data and sender_id.isdigit():
            from pymongo import ReturnDocument

            stored_data = self.chat.find_one_and_update(
                {"sender_id": int(sender_id)},
                {"$set": {"sender_id": str(sender_id)}},
                return_document=ReturnDocument.AFTER,
            )

        if not stored_data:
            return

        events = self._events_from_serialized_tracker_data(stored_data)
        if not self.load_events_from_previous_conversation_sessions:
            events = self._events_since_last_session_begins(events)

        return DialogueStateTracer.from_dict(sender_id, events, self.domain.slots)

    def keys(self) -> Iterable[Text]:
        """Returns sender_ids of the Mongo Tracker Store"""
        return [c["sender_id"] for c in self.chat.find()]


def _create_sequence(table_name: Text) -> "Sequence":
    """Creates a sequence object for a specific table name.

    If using Oracle you will need to create a sequence in your database,
    as described here: https://convo.com/docs/convo/tracker-stores#sqltrackerstore
    Args:
        table_name: The name of the table, which gets a Sequence assigned

    Returns: A `Sequence` object
    """

    from sqlalchemy.ext.declarative import declarative_base

    order_name = f"{table_name}_seq"
    Base_Name = declarative_base()
    return sa.Sequence(order_name, metadata=Base_Name.metadata, optional=True)


def is_postgresql_db_url(url: Union[Text, "URL"]) -> bool:
    """Determine whether `url` configures a PostgreSQL connection.

    Args:
        url: SQL connection URL.

    Returns:
        `True` if `url` is a PostgreSQL connection URL.
    """
    if isinstance(url, str):
        return "postgresql" in url

    return url.drivername == "postgresql"


def generate_engine_keyword_arguments(url: Union[Text, "URL"]) -> Dict[Text, Any]:
    """Get `sqlalchemy.create_engine()` kwargs.

    Args:
        url: SQL connection URL.

    Returns:
        kwargs to be passed into `sqlalchemy.create_engine()`.
    """
    if not is_postgresql_db_url(url):
        return {}

    keyword_arguments = {}

    db_schema_name = os.environ.get(POSTGRESQL_SCHEMA_NAME)

    if db_schema_name:
        log.debug(f"Using PostgreSQL schema '{db_schema_name}'.")
        keyword_arguments["connect_args"] = {"options": f"-csearch_path={db_schema_name}"}

    # pool_size and max_overflow can be set to control the number of
    # connections that are kept in the connection pool. Not available
    # for SQLite, and only  tested for PostgreSQL. See
    # https://docs.sqlalchemy.org/en/13/core/pooling.html#sqlalchemy.pool.QueuePool
    keyword_arguments["pool_size"] = int(
        os.environ.get(POSTGRESQL_POOL_SIZE, POSTGRESQL_BY_DEFAULT_POOL_SIZE)
    )
    keyword_arguments["max_overflow"] = int(
        os.environ.get(POSTGRESQL_MAXIMUM_OVERFLOW, POSTGRESQL_BY_DEFAULT_MAXIMUM_OVERFLOW)
    )

    return keyword_arguments


def make_sure_schema_exists(session: "Session") -> None:
    """Ensure that the requested PostgreSQL schema exists in the database.

    Args:
        session: Session used to inspect the database.

    Raises:
        `ValueError` if the requested schema does not exist.
    """
    schema_name = os.environ.get(POSTGRESQL_SCHEMA_NAME)

    if not schema_name:
        return

    engine_name = session.get_bind()

    if is_postgresql_db_url(engine_name.url):
        query = sa.exists(
            sa.select([(sa.text("schema_name"))])
            .select_from(sa.text("information_schema.schemata"))
            .where(sa.text(f"schema_name = '{schema_name}'"))
        )
        if not session.query(query).scalar():
            raise ValueError(schema_name)


class SQLTrackerStorage(TrackerStorage):
    """Store which can save and retrieve trackers from an SQL database."""

    from sqlalchemy.ext.declarative import declarative_base

    Base_Name = declarative_base()

    class StructuredQueryLanguageEvent(Base_Name):
        """Represents an event in the SQL Tracker Store"""

        __tablename__ = "events"

        # `create_sequence` is needed to create a sequence for databases that
        # don't autoincrement Integer primary keys (e.g. Oracle)
        identity = sa.Column(sa.Integer, _create_sequence(__tablename__), primary_key=True)
        sender_id = sa.Column(sa.String(255), nullable=False, index=True)
        type_name = sa.Column(sa.String(255), nullable=False)
        time_stamp = sa.Column(sa.Float)
        name_of_intent = sa.Column(sa.String(255))
        action_name = sa.Column(sa.String(255))
        data = sa.Column(sa.Text)

    def __init__(
        self,
        domain: Optional[Domain] = None,
        dialect: Text = "sqlite",
        host: Optional[Text] = None,
        port: Optional[int] = None,
        db: Text = "convo.db",
        username: Text = None,
        password: Text = None,
        event_broker: Optional[CoreEventBroker] = None,
        login_db: Optional[Text] = None,
        query: Optional[Dict] = None,
    ) -> None:
        import sqlalchemy.exc

        engine_path_url = self.fetch_db_url(
            dialect, host, port, db, username, password, login_db, query
        )

        self.engine = sa.create_engine(engine_path_url, **generate_engine_keyword_arguments(engine_path_url))

        log.debug(
            f"Attempting to connect to database via '{repr(self.engine.url)}'."
        )

        # Database might take a while to come up
        while True:
            try:
                # if `login_db` has been provided, use current channel with
                # that database to create working database `db`
                if login_db:
                    self._generate_db_and_update_engine(db, engine_path_url)

                try:
                    self.Base_Name.metadata.create_all(self.engine)
                except (
                    sqlalchemy.exc.OperationalError,
                    sqlalchemy.exc.ProgrammingError,
                ) as e:
                    # Several Convo services started in parallel may attempt to
                    # create tables at the same time. That is okay so long as
                    # the first services finishes the table creation.
                    log.error(f"Could not create tables: {e}")

                self.sessionmaker = sa.orm.endpoint_session.sessionmaker(bind=self.engine)
                break
            except (
                sqlalchemy.exc.OperationalError,
                sqlalchemy.exc.IntegrityError,
            ) as error:

                log.warning(error)
                sleep(5)

        log.debug(f"Connection to SQL database '{db}' successful.")

        super().__init__(domain, event_broker)

    @staticmethod
    def fetch_db_url(
        dialect: Text = "sqlite",
        host_name: Optional[Text] = None,
        port_data: Optional[int] = None,
        db: Text = "convo.db",
        username: Text = None,
        password: Text = None,
        login_db: Optional[Text] = None,
        query: Optional[Dict] = None,
    ) -> Union[Text, "URL"]:
        """Build an SQLAlchemy `URL` object representing the parameters needed
        to connect to an SQL database.

        Args:
            dialect: SQL database type.
            host_name: Database network host.
            port_data: Database network port.
            db: Database name.
            username: User name to use when connecting to the database.
            password: Password for database user.
            login_db: Alternative database name to which initially connect, and create
                the database specified by `db` (PostgreSQL only).
            query: Dictionary of options to be passed to the dialect and/or the
                DBAPI upon connect.

        Returns:
            URL ready to be used with an SQLAlchemy `Engine` object.
        """
        from urllib import parse

        # Users might specify a url in the host
        if host_name and "://" in host_name:
            # assumes this is a complete database host name including
            # e.g. `postgres://...`
            return host_name
        elif host_name:
            # add fake scheme to properly parse components
            analyse = parse.urlsplit(f"scheme://{host_name}")

            # users might include the port in the url
            port_data = analyse.port or port_data
            host_name = analyse.hostname or host_name

        return sa.engine.url.URL(
            dialect,
            username,
            password,
            host_name,
            port_data,
            database=login_db if login_db else db,
            query=query,
        )

    def _generate_db_and_update_engine(self, db: Text, engine_url: "URL"):
        """Create databse `db` and update engine to reflect the updated `engine_url`."""

        from sqlalchemy import create_engine

        self._generate_db(self.engine, db)
        engine_url.database = db
        self.engine = create_engine(engine_url)

    @staticmethod
    def _generate_db(engine: "Engine", db: Text):
        """Create database `db` on `engine` if it does not exist."""

        import psycopg2

        connection = engine.connect()

        pointer = connection.connection.cursor()
        pointer.execute("COMMIT")
        pointer.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db}'")
        occurs = pointer.fetchone()
        if not occurs:
            try:
                pointer.execute(f"CREATE DATABASE {db}")
            except psycopg2.IntegrityError as e:
                log.error(f"Could not create database '{db}': {e}")

        pointer.shut()
        connection.shut()

    @contextlib.contextmanager
    def session_range(self):
        """Provide a transactional scope around a series of operations."""
        session_name = self.sessionmaker()
        try:
            make_sure_schema_exists(session_name)
            yield session_name
        except ValueError as e:
            convo.shared.utils.cli.printing_error_exit(
                f"Requested PostgreSQL schema '{e}' was not found in the database. To "
                f"continue, please create the schema by running 'CREATE DATABASE {e};' "
                f"or unset the '{POSTGRESQL_SCHEMA_NAME}' environment variable in order to "
                f"use the default schema. Exiting application."
            )
        finally:
            session_name.shut()

    def keys(self) -> Iterable[Text]:
        """Returns sender_ids of the SQLTrackerStorage"""
        with self.session_range() as session:
            sender_ids = session.query(self.StructuredQueryLanguageEvent.sender_id).distinct().all()
            return [sender_id for (sender_id,) in sender_ids]

    def recover(self, sender_id: Text) -> Optional[DialogueStateTracer]:
        """Create a tracker from all previously stored events."""

        with self.session_range() as session:

            serialised_events_data = self._event_fetch_query(session, sender_id).all()

            events = [json.loads(event.data) for event in serialised_events_data]

            if self.domain and len(events) > 0:
                log.debug(f"Recreating tracker from sender id '{sender_id}'")
                return DialogueStateTracer.from_dict(
                    sender_id, events, self.domain.slots
                )
            else:
                log.debug(
                    f"Can't retrieve tracker matching "
                    f"sender id '{sender_id}' from SQL storage. "
                    f"Returning `None` instead."
                )
                return None

    def _event_fetch_query(self, session: "Session", sender_id: Text) -> "Query":
        """Provide the query to retrieve the conversation events for a specific sender.

        Args:
            session: Current database session.
            sender_id: Sender id whose conversation events should be retrieved.

        Returns:
            Query to get the conversation events.
        """
        # Subquery to find the timestamp of the latest `SessionBegan` event
        session_start_fetch_sub_query = (
            session.query(sa.func.max(self.StructuredQueryLanguageEvent.time_stamp).label("session_start"))
            .filter(
                self.StructuredQueryLanguageEvent.sender_id == sender_id,
                self.StructuredQueryLanguageEvent.type_name == SessionBegan.type_name,
            )
            .subquery()
        )

        event_query = session.query(self.StructuredQueryLanguageEvent).filter(
            self.StructuredQueryLanguageEvent.sender_id == sender_id
        )
        if not self.load_events_from_previous_conversation_sessions:
            event_query = event_query.filter(
                # Find events after the latest `SessionBegan` event or return all
                # events
                sa.or_(
                    self.StructuredQueryLanguageEvent.time_stamp >= session_start_fetch_sub_query.c.session_start,
                    session_start_fetch_sub_query.c.session_start.is_(None),
                )
            )

        return event_query.order_by(self.StructuredQueryLanguageEvent.time_stamp)

    def save(self, tracker: DialogueStateTracer) -> None:
        """Update database with events from the current conversation."""

        if self.event_broker:
            self.fetch_stream_events(tracker)

        with self.session_range() as session:
            # only store recent events
            events = self._extra_events(session, tracker)

            for event in events:
                data_set = event.as_dictionary()
                intentions = (
                    data_set.get("parse_data", {}).get("intent", {}).get(KEY_INTENT_NAME)
                )
                act = data_set.get("name")
                time_stamp = data_set.get("timestamp")

                # noinspection PyArgumentList
                session.add(
                    self.StructuredQueryLanguageEvent(
                        sender_id=tracker.sender_id,
                        type_name=event.type_name,
                        timestamp=time_stamp,
                        name_of_intent=intentions,
                        action_name=act,
                        data=json.dumps(data_set),
                    )
                )
            session.commit()

        log.debug(f"Tracker with sender_id '{tracker.sender_id}' stored to database")

    def _extra_events(
        self, session: "Session", tracker: DialogueStateTracer
    ) -> Iterator:
        """Return events from the tracker which aren't currently stored."""

        no_of_events_since_end_session = self._event_fetch_query(
            session, tracker.sender_id
        ).count()
        return itertools.islice(
            tracker.events, no_of_events_since_end_session, len(tracker.events)
        )


class FailSafeTrackerStorage(TrackerStorage):
    """Wraps a tracker store so that we can fallback to a different tracker store in
    case of errors."""

    def __init__(
        self,
        tracker_store: TrackerStorage,
        on_tracker_store_error: Optional[Callable[[Exception], None]] = None,
        fallback_tracker_store: Optional[TrackerStorage] = None,
    ) -> None:
        """Create a `FailSafeTrackerStorage`.

        Args:
            tracker_store: Primary tracker store.
            on_tracker_store_error: Callback which is called when there is an error
                in the primary tracker store.
        """

        self._fallback_tracker_store: Optional[TrackerStorage] = fallback_tracker_store
        self._tracker_store = tracker_store
        self._on_tracker_store_error = on_tracker_store_error

        super().__init__(tracker_store.domain, tracker_store.event_broker)

    @property
    def domain(self) -> Optional[Domain]:
        return self._tracker_store.domain

    @domain.setter
    def domain(self, domain: Optional[Domain]) -> None:
        self._tracker_store.domain = domain

        if self._fallback_tracker_store:
            self._fallback_tracker_store.domain = domain

    @property
    def fallback_tracker_storage(self) -> TrackerStorage:
        if not self._fallback_tracker_store:
            self._fallback_tracker_store = InMemoryTrackerStorage(
                self._tracker_store.domain, self._tracker_store.event_broker
            )

        return self._fallback_tracker_store

    def on_tracker_storage_err(self, error: Exception) -> None:
        if self._on_tracker_store_error:
            self._on_tracker_store_error(error)
        else:
            log.error(
                f"Error happened when trying to save conversation tracker to "
                f"'{self._tracker_store.__class__.__name__}'. Falling back to use "
                f"the '{InMemoryTrackerStorage.__name__}'. Please "
                f"investigate the following error: {error}."
            )

    def recover(self, sender_id: Text) -> Optional[DialogueStateTracer]:
        try:
            return self._tracker_store.recover(sender_id)
        except Exception as e:
            self.on_tracker_storage_err(e)
            return None

    def keys(self) -> Iterable[Text]:
        try:
            return self._tracker_store.keys()
        except Exception as e:
            self.on_tracker_storage_err(e)
            return []

    def save(self, tracker: DialogueStateTracer) -> None:
        try:
            self._tracker_store.save(tracker)
        except Exception as e:
            self.on_tracker_storage_err(e)
            self.fallback_tracker_storage.save(tracker)


def _generate_from_endpoint_configuration(
    endpoint_config: Optional[EndpointConfiguration] = None,
    domain_name: Optional[Domain] = None,
    event_broker: Optional[CoreEventBroker] = None,
) -> "TrackerStorage":
    """Given an endpoint configuration, create a proper tracker store object."""

    domain_name = domain_name or Domain.empty()

    if endpoint_config is None or endpoint_config.type is None:
        # default tracker store if no type is set
        tracker_storage = InMemoryTrackerStorage(domain_name, event_broker)
    elif endpoint_config.type.lower() == "redis":
        tracker_storage = RedisTrackerStorage(
            domain=domain_name,
            host=endpoint_config.url,
            event_broker=event_broker,
            **endpoint_config.kwargs,
        )
    elif endpoint_config.type.lower() == "mongod":
        tracker_storage = MongoTrackerStorage(
            domain=domain_name,
            host=endpoint_config.url,
            event_broker=event_broker,
            **endpoint_config.kwargs,
        )
    elif endpoint_config.type.lower() == "sql":
        tracker_storage = SQLTrackerStorage(
            domain=domain_name,
            host=endpoint_config.url,
            event_broker=event_broker,
            **endpoint_config.kwargs,
        )
    elif endpoint_config.type.lower() == "dynamo":
        tracker_storage = DynamoTrackerStorage(
            domain=domain_name, event_broker=event_broker, **endpoint_config.kwargs
        )
    else:
        tracker_storage = _load_from_module_name_in_endpoint_configurations(
            domain_name, endpoint_config, event_broker
        )

    log.debug(f"Connected to {tracker_storage.__class__.__name__}.")

    return tracker_storage


def _load_from_module_name_in_endpoint_configurations(
    domain: Domain, store: EndpointConfiguration, event_broker: Optional[CoreEventBroker] = None
) -> "TrackerStorage":
    """Initializes a custom tracker.

    Defaults to the InMemoryTrackerStorage if the module path can not be found.

    Args:
        domain: defines the universe in which the assistant operates
        store: the specific tracker store
        event_broker: an event broker to publish events

    Returns:
        a tracker store from a specified type in a stores endpoint configuration
    """

    try:
        tracker_storage_class = convo.shared.utils.common.class_name_from_module_path(
            store.type
        )
        init_arguments = convo.shared.utils.common.args_of(tracker_storage_class.__init__)
        if "url" in init_arguments and "host" not in init_arguments:
            # DEPRECATION EXCEPTION - remove in 2.1
            raise Exception(
                "The `url` initialization argument for custom tracker stores has "
                "been removed. Your custom tracker store should take a `host` "
                "argument in its `__init__()` instead."
            )
        else:
            store.kwargs["host"] = store.url

        return tracker_storage_class(
            domain=domain, event_broker=event_broker, **store.kwargs
        )
    except (AttributeError, ImportError):
        convo.shared.utils.io.raising_warning(
            f"Tracker store with type '{store.type}' not found. "
            f"Using `InMemoryTrackerStorage` instead."
        )
        return InMemoryTrackerStorage(domain)
