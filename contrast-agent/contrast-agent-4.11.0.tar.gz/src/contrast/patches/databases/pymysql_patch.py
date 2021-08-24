# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.extern.wrapt import register_post_import_hook

import contrast
from contrast.patches.databases import dbapi2
from contrast.utils import inventory_utils, patch_utils

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")

PYMYSQL = "pymysql"
VENDOR = "MySQL"


def build_connect_patch(orig_func, _):
    def connect(*args, **kwargs):
        """Record DB inventory for MySQL"""
        try:
            context = contrast.CS__CONTEXT_TRACKER.current()
            if context is not None:
                db_inventory = dict(
                    vendor=VENDOR,
                    host=kwargs.get("host"),
                    port=kwargs.get("port"),
                    database=kwargs.get("db"),
                )
                inventory_utils.append_db(context.activity, db_inventory)
        except Exception:
            logger.exception("Failed to add inventory for %s", VENDOR)

        return orig_func(*args, **kwargs)

    return connect


def instrument_pymysql(pymysql):
    """
    Note: Unlike other sql drivers, pymysql does not have an executescript method.
    """
    patch_utils.build_and_apply_patch(pymysql, "connect", build_connect_patch)
    dbapi2.instrument_cursor(PYMYSQL, pymysql.cursors.Cursor)


def register_patches():
    register_post_import_hook(instrument_pymysql, PYMYSQL)
