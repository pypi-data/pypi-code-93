# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
"""
Implements a single API for instrumenting all dbapi2-compliant modules
"""
from contrast.applies.sqli import apply_rule
from contrast.utils.decorators import fail_safely
from contrast.utils.patch_utils import build_and_apply_patch


def build_cursor_method_patch(orig_func, patch_policy, database, adapter):
    def patched_method(*args, **kwargs):
        return apply_rule(database, adapter, orig_func, args, kwargs)

    return patched_method


def _instrument_cursor_method(database, cursor, method_name):
    build_and_apply_patch(
        cursor,
        method_name,
        build_cursor_method_patch,
        (database, method_name),
    )


def instrument_cursor(database, cursor):
    """
    Instruments a dbapi2-compliant database cursor class

    @param database: Name of the database module being patched (e.g. "sqlite3")
    @param cursor: Reference to cursor class to be instrumented
    """
    _instrument_cursor_method(database, cursor, "execute")
    _instrument_cursor_method(database, cursor, "executemany")


def instrument_executescript(database, cursor):
    """
    Instruments the `executescript` method of a database cursor class

    The executescript method is non-standard but is provided by some drivers
    including sqlite3.

    @param database: Name of the database module being patched (e.g. "sqlite3")
    @param cursor: Reference to cursor class to be instrumented
    """
    _instrument_cursor_method(database, cursor, "executescript")


@fail_safely("failed to instrument database adapter")
def instrument_adapter(database, adapter):
    """
    In some cases (SQLAlchemy), we need to instrument an unknown PEP-249 compliant
    adapter. We only have a reference to the adapter module, and we can't make any
    assumptions about the existence of `adapter.Cursor`, since this is not guaranteed
    by the spec.

    We are only guaranteed the following:
    - the adapter has a `connection()` method, which returns an instance of Connection
    - the Connection object has a `cursor()` method, which returns an instance of Cursor
    - the Cursor has `execute()` and `executemany()` methods

    This requires a somewhat roundabout instrumentation strategy:
    - on the first call to adapter.connect(), we can access the Connection class
    - on the first call to Connection.cursor(), we can access the Cursor class
    - this lets us instrument Cursor.execute() and Cursor.executemany()
    """

    @fail_safely("failed to instrument database cursor object")
    def safe_instrument_cursor(cursor_instance):
        """
        Safely instrument a Cursor class given an instance of that class
        """
        cursor_class = type(cursor_instance)
        instrument_cursor(database, cursor_class)

    @fail_safely("failed to instrument database connection object")
    def safe_instrument_connection(connection_instance):
        """
        Safely instrument a Connection class given an instance of that class
        """
        connection_class = type(connection_instance)
        build_and_apply_patch(connection_class, "cursor", build_cursor_patch)

    def build_cursor_patch(orig_func, _):
        def cursor_patch(*args, **kwargs):
            """
            Patch for dbapi_adapter.connection().cursor()

            This patch will ensure that the returned Cursor object's class will have
            `execute` and `executemany` instrumented.
            """
            cursor = orig_func(*args, **kwargs)
            safe_instrument_cursor(cursor)
            return cursor

        return cursor_patch

    def build_connect_patch(orig_func, _):
        def connect_patch(*args, **kwargs):
            """
            Patch for dbapi_adapter.connection()

            This patch will ensure that the returned Connection object's class will have
            `cursor_patch` applied to its cursor() method.
            """
            connection = orig_func(*args, **kwargs)
            safe_instrument_connection(connection)
            return connection

        return connect_patch

    build_and_apply_patch(adapter, "connect", build_connect_patch)
