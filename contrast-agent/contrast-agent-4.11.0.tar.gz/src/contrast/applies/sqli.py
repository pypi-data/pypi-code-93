# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
"""
Rule applicator for SQLi for dbapi2-compliant modules
"""
import contrast
from contrast.agent import scope
from contrast.agent.protect.rule.sqli_rule import SqlInjection
from contrast.agent.policy.loader import Policy
from contrast.agent.assess.policy.analysis import skip_analysis
from contrast.agent.assess.policy import trigger_policy
from contrast.agent.settings_state import SettingsState
from contrast.applies import (
    DATABASE_SQLITE,
    DATABASE_PG,
    DATABASE_MYSQL,
    DATABASE_SQL_ALCHEMY,
)
from contrast.utils import inventory_utils
from contrast.utils.decorators import fail_safely


# This represents a map of adapters (modules) to underlying db technologies
# The adapter name is used for policy lookup/trace reporting purposes, but the
# technology name is used for inventory reporting.
ADAPTER_TO_DATABASE = {
    "sqlite3": DATABASE_SQLITE,
    "pysqlite2.dbapi2": DATABASE_SQLITE,
    "psycopg2": DATABASE_PG,
    "pymysql": DATABASE_MYSQL,
    "sqlalchemy": DATABASE_SQL_ALCHEMY,
}


@fail_safely("Error running SQLi assess rule")
def assess_rule(context, adapter, method, result, args, kwargs):
    """
    Apply assess SQLi rule

    @param context: Current RequestContext instance
    @param adapter: String representing the adapter module (e.g. "sqlite3")
    @param method: String representing the database method (e.g. "execute")
    @param result: Object representing result of database action
    @param args: The args tuple passed to the original database function
    @param kwargs: The kwargs dict passed to the original database function
    """
    if scope.in_trigger_scope():
        return

    context.activity.query_count += 1

    policy = Policy()

    rule = policy.triggers["sql-injection"]
    trigger_nodes = rule.find_trigger_nodes("{}.Cursor".format(adapter), method)

    with scope.trigger_scope():
        trigger_policy.apply(rule, trigger_nodes, result, args, kwargs)


def apply_rule(adapter, method, orig_func, args, kwargs):
    """
    Common API for applying SQLi rule (applies both protect and assess rules)

    Applies the assess rule if assess is enabled. If protect is enabled,
    applies the protect rule. Important caveats:
      - neither rule will be applied if there is not an active request context
      - the assess rule will not be applied if we are already in scope

    The protect rule *must* be applied prior to calling the original function.
    This is the only way that we can raise a SecurityException if the rule is
    in BLOCK mode.

    The assess rule *must* be applied even if the original function results in
    an exception. Otherwise we won't detect vulnerable dataflows that may have
    just happened to result in an exception under testing.

    @param adapter: String representing the adapter (e.g. "sqlite3")
    @param method: String representing the database method (e.g. "execute")
    @param orig_func: Original function (i.e. the one replaced by the patch)
    @param *args: The *args passed to the original database function
    @param **kwargs: The **kwargs passed to the original database function

    @return: Returns the object that is returned by calling orig_func
    """
    context = contrast.CS__CONTEXT_TRACKER.current()

    if context is not None:
        _report_inventory(context, adapter)
        _protect_rule(context, adapter, method, args, kwargs)

    try:
        result = orig_func(*args, **kwargs)
    except Exception:
        result = None
        raise
    finally:
        if not skip_analysis(context):
            assess_rule(context, adapter, method, result, args, kwargs)

    return result


@fail_safely("Error during database inventory reporting")
def _report_inventory(context, adapter):
    """
    We report database inventory information every time we see any database call. This
    is the only way we can get TS flowmap working properly.

    Eventually, we'll need to be able to report the host, port, and database name too.
    (TODO: PYT-1698)
    """
    vendor = ADAPTER_TO_DATABASE.get(adapter)
    if not vendor:
        return

    db_inventory = dict(vendor=vendor)
    inventory_utils.append_db(context.activity, db_inventory)


@fail_safely("Error running SQLi protect rule")
def _protect_rule(context, adapter, method, args, kwargs):
    """
    Run protect SQLi analysis if it's enabled.
    """
    if not SettingsState().is_protect_enabled() or len(args) <= 1:
        return

    # args[0] is self, args[1] is the query
    sql = args[1]

    database = ADAPTER_TO_DATABASE.get(adapter, adapter)

    # TODO: PYT-986: remove creating fake policy node and patch loc policy
    from contrast.agent.policy.patch_location_policy import PatchLocationPolicy
    from contrast.agent.policy.trigger_node import TriggerNode

    trigger_node = TriggerNode(database, "unused", True, method, "ARG_0")
    patch_policy = PatchLocationPolicy(trigger_node)

    rule = SettingsState().defend_rules.get(SqlInjection.NAME)
    rule.protect(patch_policy, sql, args, kwargs)
