"""
Task implementations
"""
import contextlib
import dataclasses
import logging
import typing

from workflows import bases

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class NoOp(bases.Task):
    """Task that does nothing; can be a stub for outputs"""

    def execute(self, context):
        self.validate()


def get_db_connection(database_url):
    """
    Given a connection string, return a DB conn. Written separately to
    allow monkey-patching to use a different database library
    """
    import psycopg2  # import here to avoid requiring it

    return psycopg2.connect(database_url)


@dataclasses.dataclass
class Sql(bases.Task):
    """
    A SQL transform. Connects to a database using DATABASE_URL provided in the
     context and executes the given SQL.
    """

    sql: str = None
    class_parameters = ("DATABASE_URL",)

    def execute(self, context):
        # the context manager commits the transaction on exit
        with get_db_connection(context["DATABASE_URL"]) as conn:
            conn.cursor().execute(self.sql)
            self.validate({"conn": conn})


@dataclasses.dataclass
class Python(bases.Task):
    """A Python transform. Calls the run method."""

    run: typing.Callable = None

    def execute(self, context):
        # Open a connection if the task requests one. Doing so allows
        # the validations to use it and roll back the transaction if needed.
        if "DATABASE_URL" in context:
            connection = get_db_connection(context["DATABASE_URL"])
        else:
            connection = contextlib.nullcontext()

        with connection as conn:
            context["conn"] = conn
            self.run(context)
            self.validate(context)


@dataclasses.dataclass
class BigQuerySql(bases.Task):
    """
    A BigQuery SQL transform. Connects BigQuery and executes the given SQL.
    """

    sql: str = None
    class_parameters = ("GCP_PROJECT",)

    def execute(self, context):
        from google.cloud import bigquery  # import here to avoid requiring it
        from google.cloud.bigquery import dbapi  # import here to avoid requiring it

        client = bigquery.Client(project=context["GCP_PROJECT"])
        query = client.query(self.sql)
        # wait for it to run
        query.result()
        mb_billed = query.total_bytes_billed / 1024 / 1024
        LOGGER.info(f"Query finished, processed {mb_billed} MB")
        self.validate({"client": client, "conn": dbapi.Connection(client)})
