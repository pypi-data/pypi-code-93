# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.extern.wrapt import register_post_import_hook
import sys
import contrast
from contrast.agent.policy import patch_manager
from contrast.patches.databases import dbapi2
from contrast.utils import inventory_utils, patch_utils

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


SQLITE3 = "sqlite3"
PYSQLITE2_DBAPI2 = "pysqlite2.dbapi2"
VENDOR = "SQLite3"


def build_connect_patch(orig_func, _):
    def connect(*args, **kwargs):
        """Record DB inventory for SQLite3 connection"""
        try:
            context = contrast.CS__CONTEXT_TRACKER.current()
            if context is not None:
                # sqlite does not use a server, so no need for host/port
                database = kwargs.get("database") or (
                    args[0] if len(args) > 0 else "unknown"
                )
                db_inventory = dict(vendor=VENDOR, database=database)
                inventory_utils.append_db(context.activity, db_inventory)
        except Exception:
            logger.exception("Failed to add inventory for %s", VENDOR)

        return orig_func(*args, **kwargs)

    return connect


def instrument_sqlite_dbapi2(sqlite3):
    dbapi2.instrument_cursor(SQLITE3, sqlite3.Cursor)
    dbapi2.instrument_executescript(SQLITE3, sqlite3.Cursor)
    patch_utils.build_and_apply_patch(sqlite3, "connect", build_connect_patch)


def instrument_pysqlite2_dbapi2(pysqlite2):
    """Supports the older pysqlite module in Py2"""
    dbapi2.instrument_cursor(PYSQLITE2_DBAPI2, pysqlite2.Cursor)
    dbapi2.instrument_executescript(PYSQLITE2_DBAPI2, pysqlite2.Cursor)
    patch_utils.build_and_apply_patch(pysqlite2, "connect", build_connect_patch)


def register_patches():
    register_post_import_hook(instrument_sqlite_dbapi2, SQLITE3)
    register_post_import_hook(instrument_pysqlite2_dbapi2, PYSQLITE2_DBAPI2)


def reverse_patches():
    sqlite3 = sys.modules.get(SQLITE3)
    if sqlite3:
        patch_manager.reverse_patches_by_owner(sqlite3)
        patch_manager.reverse_patches_by_owner(sqlite3.Cursor)

    psqlite = sys.modules.get(PYSQLITE2_DBAPI2)
    if psqlite:
        patch_manager.reverse_patches_by_owner(psqlite)
        patch_manager.reverse_patches_by_owner(psqlite.Cursor)
