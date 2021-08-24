# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
"""
Database adapter patch for psycopg2.
This module's cursor doesn't have an `executescript` method.
"""

import os
from contrast.extern.wrapt import register_post_import_hook

import contrast
from contrast.patches.databases import dbapi2
from contrast.utils import inventory_utils, patch_utils

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")

PSYCOPG2 = "psycopg2"
VENDOR = "PostgreSQL"
PSYCOPG2_EXTENSIONS = "psycopg2.extensions"
CONNECT = "connect"


def build_connect_patch(orig_func, _):
    """
    Record DB inventory for a Postgres connection.

    Here we make a good effort to find connection params. There are several ways that these can be set,
    in the following order of priority (using dbname as an example):
    - using the `connection_factory` kwarg
    - as a kwarg itself - `dbname` or the deprecated `database`
    - via the dbname parameter in the dsn string
    - with the PGDATABASE environment variable

    Newer versions of psycopg2 (v2.7, ~2017) support connection.get_dsn_parameters, which provides
    a dictionary of the parsed connection params - we're interested in `dbname`.

    For now, it's still possible for us to miss the dbname (i.e. an old version of psycopg2 using
    the dsn string only), but this is unlikely and it would only affect inventory.
    """

    def connect(*args, **kwargs):
        connection = orig_func(*args, **kwargs)
        try:
            context = contrast.CS__CONTEXT_TRACKER.current()
            if context is not None:
                host, port, dbname = _get_inventory_params(connection, kwargs)
                db_inventory = dict(
                    vendor=VENDOR, host=host, port=port, database=dbname
                )
                inventory_utils.append_db(context.activity, db_inventory)
        except Exception:
            logger.exception("Failed to add inventory for %s", VENDOR)

        return connection

    return connect


def _get_inventory_params(connection, kwargs):
    """
    Get the host, port, and dbname for the current connection. This is used for inventory reporting.
    """
    dsn_params = getattr(connection, "get_dsn_parameters", lambda: {})()
    host = (
        dsn_params.get("host")
        or kwargs.get("host")
        or os.environ.get("PGHOST", "unknown_host")
    )
    port = (
        dsn_params.get("port")
        or kwargs.get("port")
        or os.environ.get("PGPORT", "unknown_port")
    )
    dbname = (
        dsn_params.get("dbname")
        or kwargs.get("dbname")
        or kwargs.get("database")
        or os.environ.get("PGDATABASE", "unknown_database")
    )
    return host, port, dbname


def instrument_psycopg2(psycopg2):
    patch_utils.build_and_apply_patch(psycopg2, "connect", build_connect_patch)


def instrument_extensions(psycopg2_extensions):
    """
    psycopg2 allows for custom cursor objects. We can still handle these as long as they
    subclass the base/default cursor provided by psycopg2 and use super() to call the original
    execute* methods. This seems to be the only possible use case, so we'll always have
    execute instrumented.

    see https://www.psycopg.org/docs/advanced.html#subclassing-connection

    Also note that psycopg2 includes several convenient extensions to dbapi2:
    - psycopg2.extras.execute_batch
    - psycopg2.extras.execute_values
    These both call `execute` internally
    """
    dbapi2.instrument_cursor(PSYCOPG2, psycopg2_extensions.cursor)


def register_patches():
    register_post_import_hook(instrument_psycopg2, PSYCOPG2)
    register_post_import_hook(instrument_extensions, PSYCOPG2_EXTENSIONS)
