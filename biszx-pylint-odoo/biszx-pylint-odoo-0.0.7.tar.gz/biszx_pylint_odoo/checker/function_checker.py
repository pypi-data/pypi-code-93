from typing import Any
import astroid
import re

from pylint import interfaces
from pylint.checkers import BaseChecker, utils

from .. import settings, messages


class FunctionChecker(BaseChecker):
    __implements__ = interfaces.IAstroidChecker

    name = settings.CHECKER_NAME
    msgs = messages.FUNCTION_CHECKER_MSGS

    @utils.check_messages('biszx-compute-func-name',
                          'biszx-onchange-func-name',
                          'biszx-constrains-func-name')
    def visit_functiondef(self, node: astroid.FunctionDef):
        decorators = node.decorators
        if not decorators:
            return

        find = ('depends', 'onchange', 'constrains')
        for decorator in decorators.nodes:
            if (
                isinstance(decorator, astroid.Call)
                and decorator.func.expr.name == 'api'
                and (key := decorator.func.attrname) in find
            ):
                self._check_match_func_name(
                    node,
                    key,
                    node.name
                )

    @utils.check_messages('biszx-default-func-name',
                          'biszx-domain-func-name')
    def visit_assign(self, node: astroid.Assign):
        value = node.value
        if (
            not value
            or not isinstance(value, astroid.Call)
            or not value.keywords
            or not isinstance(value.func, astroid.Attribute)
            or not isinstance(value.func.expr, astroid.Name)
            or value.func.expr.name != 'fields'
        ):
            return

        find = ('default', 'search', 'domain')
        for keyword in value.keywords:
            if (key := keyword.arg) in find:
                arg = keyword.value
                if isinstance(arg, astroid.Lambda):
                    self._check_match_func_name(
                        arg,
                        key,
                        arg.body.func.attrname
                    )
                elif isinstance(arg, astroid.Name):
                    self._check_match_func_name(arg, key, arg.name)
                elif key == 'search' and isinstance(arg, astroid.Const):
                    self._check_match_func_name(arg, key, arg.value)

    def _check_match_func_name(
        self,
        node: Any,
        key: str,
        name: str,
    ) -> None:
        check_value = {
            'search': {
                're': '^_search_*',
                'msg_id': 'biszx-search-func-name'
            },
            'default': {
                're': '^_default_*',
                'msg_id': 'biszx-default-func-name'
            },
            'depends': {
                're': '^_compute_*',
                'msg_id': 'biszx-compute-func-name'
            },
            'onchange': {
                're': '^_onchange_*',
                'msg_id': 'biszx-onchange-func-name'
            },
            'constrains': {
                're': '^_check_*',
                'msg_id': 'biszx-constrains-func-name'
            },
            'domain': {
                're': '^_domain_*',
                'msg_id': 'biszx-domain-func-name'
            },
        }
        value = check_value[key]
        if not re.match(value['re'], name):
            self.add_message(value['msg_id'], node=node)
