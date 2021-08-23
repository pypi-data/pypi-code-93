import functools
import json
import logging

LOGGER = logging.getLogger(__name__)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({"severity": record.levelname, "message": super().format(record)})


def close_on_exception(func):
    """
    A wrapper to close the database connection if a DB error occurs,
    so that it will get re-opened on the next use.
    Squashes the exception and logs it.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        from django import db

        try:
            func(*args, **kwargs)
        except db.OperationalError:
            LOGGER.error("Database error, closing connection", exc_info=True)
            db.connection.close()
            assert db.connection.closed_in_transaction is False, (
                "Could not close connection, probably because this wrapper "
                "was used inside an transaction.atomic() block."
            )

    return wrapper
