from .base import Unset


def validate(type_, value, types):
    return list(type_.visit(ValidationVisitor(types), value))


class ValidationVisitor:

    def __init__(self, types):
        self.types = types

    def visit_any(self, node, value):
        return []

    def visit_null(self, node, value):
        if value is not None:
            yield (), 'should be null'

    def visit_string(self, node, value):
        if not isinstance(value, str):
            yield (), 'should be a string'

    def visit_integer(self, node, value):
        if not isinstance(value, int):
            yield (), 'should be an integer'

    def visit_boolean(self, node, value):
        if not isinstance(value, bool):
            yield (), 'should be a boolean'

    def visit_object(self, node, value):
        if not isinstance(value, dict):
            yield (), 'should be an object'
            return

        for name, type_ in node.fields.items():
            if name in node.optional_keys and name not in value:
                continue
            elif name not in value:
                yield (name,), "value missing"
            else:
                for path, msg in type_.visit(self, value[name]):
                    yield (name, *path), msg

    def visit_list(self, node, value):
        if not isinstance(value, list):
            yield (), 'should be a list'
            return

        for index, item in enumerate(value):
            for path, msg in node.type.visit(self, item):
                yield (index, *path), msg

    def visit_const(self, node, value):
        if not node.value == value:
            yield ((), 'should be %r' % node.value)

    def visit_unset(self, node, value):
        if not value == Unset.UNSET:
            yield ((), 'should be unset')

    def visit_reference(self, node, value):
        type_ = self.types[node.name]
        return type_.visit(self, value)

    def visit_oneof(self, node, value):
        if not any(not list(type_.visit(self, value)) for type_ in node.types):
            text = ", ".join(str(type_) for type_ in node.types)
            yield ((), f'must be one of { text }')
