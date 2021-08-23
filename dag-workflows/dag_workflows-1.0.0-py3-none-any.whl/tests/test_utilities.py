import logging

import pytest
from django.db import connection

from .. import utilities


def test_logs():
    record = logging.LogRecord("test", logging.INFO, "path", 1, "message", {}, None)
    message = utilities.JsonFormatter().format(record)
    assert message == '{"severity": "INFO", "message": "message"}'


@pytest.mark.django_db(transaction=True)
def test_close_on_exception():
    @utilities.close_on_exception
    def example_disconnect():
        with connection.cursor() as cursor:

            # kill the current connection, which will raise a django.db.OperationalError
            cursor.execute("select pg_terminate_backend(pg_backend_pid())")

            # which means we never get here
            assert False, "exception was not raised"  # pragma: no cover

    # this will cause a disconnect:
    example_disconnect()

    # but the exception is caught, and on retry the database reconnects:
    with connection.cursor() as cursor:
        cursor.execute("select 1")
