# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.middlewares.route_coverage.coverage_utils import (
    CoverageUtils,
    DEFAULT_ROUTE_METHODS,
)

DEFAULT_ROUTE_METHODS = DEFAULT_ROUTE_METHODS + ("PUT", "PATCH", "DELETE")


def create_bottle_routes(app):
    """
    Returns all the routes registered to a Bottle app as a dict
    :param app: Bottle app
    :return: dict {route_id:  RouteCoverage}
    """
    routes = {}
    for rule in app.routes:
        view_func = rule.callback
        route = build_bottle_route(rule.rule, view_func)
        route_id = str(id(view_func))

        for method_type in DEFAULT_ROUTE_METHODS:
            key = CoverageUtils.build_key(route_id, method_type)
            routes[key] = CoverageUtils.build_route_coverage(
                verb=method_type,
                url=CoverageUtils.get_normalized_uri(str(rule.rule)),
                route=route,
            )
    return routes


def build_bottle_route(view_func_name, view_func):
    view_func_args = CoverageUtils.build_args_from_function(view_func)
    return view_func_name + view_func_args
