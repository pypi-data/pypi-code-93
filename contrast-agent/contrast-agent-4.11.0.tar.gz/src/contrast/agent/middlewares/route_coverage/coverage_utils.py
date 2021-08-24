# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import re
import ast
import textwrap
from inspect import getsource, isclass
from types import FunctionType, MethodType

from contrast.api.dtm_pb2 import RouteCoverage

DEFAULT_ROUTE_METHODS = ("GET", "POST")


class CoverageUtils(object):
    """
    Rules for coverage:

    - new routes on init get count 0
    - new routes after init get count 1 per context
    - routes without a method type specified on init are ['GET', 'POST']
    - a route needs verb, route, url, and count
    - url should be normalized uri
    - route should be the path to the view function (aka controller for Java people)
    - one method type per route

    Example:
          GET /blog/foo/bar - app.blogs.find(request, ) 0
    """

    # 1 or more digits, then a group: either '/' or end of string
    DIGITS_ONLY_PATH_COMPONENT = r"/\d+(/|$)"

    @staticmethod
    def get_normalized_uri(path):
        """
        A best-effort to remove client-specific information from the path.

        Example:
        /user/123456/page/12 -> /user/{n}/page/{n}
        """
        return re.sub(CoverageUtils.DIGITS_ONLY_PATH_COMPONENT, r"/{n}\1", path)

    @staticmethod
    def build_route_coverage(**kwargs):
        route_coverage = RouteCoverage()
        route_coverage.verb = kwargs.get("verb", "GET")
        route_coverage.url = kwargs.get("url", "")
        route_coverage.route = kwargs.get("route", "")

        return route_coverage

    @staticmethod
    def check_for_http_decorator(func):
        """
        Grabs the require_http_methods decorator from a view function call via inspect

        NOTE: this only works for require_http_methods; it does not currently work for require_GET,
        require_POST, require_safe
        """
        method_types = {}

        if func is None:
            return method_types

        def visit_function_def(node):
            for n in node.decorator_list:
                if isinstance(n, ast.Call) and hasattr(n, "func"):
                    node_func = n.func

                    # decorator name which should be require_http_methods
                    if (
                        hasattr(node_func, "id")
                        and node_func.id == "require_http_methods"
                    ):
                        name = (
                            node_func.attr
                            if isinstance(node_func, ast.Attribute)
                            else node_func.id
                        )
                        method_types[name] = [s.s for s in n.args[0].elts]
                        return

        node_iter = ast.NodeVisitor()
        node_iter.visit_FunctionDef = visit_function_def
        node_source = textwrap.dedent(getsource(func))
        node_iter.visit(ast.parse(node_source))

        return method_types

    @staticmethod
    def get_lowest_function_call(func):
        if isclass(func) or func.__closure__ is None:
            return func
        closure = (c.cell_contents for c in func.__closure__)
        return next(
            (c for c in closure if isinstance(c, (FunctionType, MethodType))), None
        )

    @staticmethod
    def build_args_from_function(func):
        """
        Attempts to grab argument names from the function definition.

        Defaults to () if none exist
        If there is no view function, like in the case of a pure WSGI app, then the func will
        be a string like '/sqli' and we just return that.

        func_code is for PY2 and __code__ is for PY3
        """
        method_arg_names = "()"
        if func is not None and hasattr(func, "func_code"):
            method_arg_names = str(
                func.func_code.co_varnames[0 : func.func_code.co_argcount]
            ).replace("'", "")
        elif func is not None and hasattr(func, "__code__"):
            method_arg_names = str(
                func.__code__.co_varnames[0 : func.__code__.co_argcount]
            ).replace("'", "")
        elif isinstance(func, str):
            method_arg_names = func

        return method_arg_names

    @staticmethod
    def build_key(route_id, method):
        return "_".join([route_id, method])
