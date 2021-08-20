import astroid
from pylint import interfaces
from pylint.checkers import utils

from .base_checker import BaseChecker
from .. import messages


class FieldChecker(BaseChecker):
    __implements__ = interfaces.IAstroidChecker

    msgs: dict = messages.FIELD_CHECKER_MSGS
    validators: dict = {
        'Many2one': {
            're': '^.*_id$',
            'msg_id': 'biszx-relation2one-field-name'
        },
        'One2many': {
            're': '^.*_ids$',
            'msg_id': 'biszx-relation2many-field-name'
        },
        'Many2many': {
            're': '^.*_ids$',
            'msg_id': 'biszx-relation2many-field-name'
        },
        'Boolean': {
            're': '^is_*',
            'msg_id': 'biszx-boolean-field-name'
        },
        'Date': {
            're': '^.*_date$',
            'msg_id': 'biszx-date-field-name'
        },
        'Datetime': {
            're': '^.*_at$',
            'msg_id': 'biszx-datetime-field-name'
        },
    }

    @utils.check_messages('biszx-relation2one-field-name',
                          'biszx-relation2many-field-name',
                          'biszx-boolean-field-name',
                          'biszx-date-field-name',
                          'biszx-datetime-field-name')
    def visit_assign(self, node: astroid.Assign):
        find: tuple = tuple(self.validators.keys())
        value = node.value
        if (
            value
            and isinstance(value, astroid.Call)
            and isinstance(value.func, astroid.Attribute)
            and isinstance(value.func.expr, astroid.Name)
            and value.func.expr.name == 'fields'
            and (key := value.func.attrname) in find
        ):
            self._validate_match_name(
                node,
                key,
                node.targets[0].name
            )
