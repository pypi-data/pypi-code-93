
class Type:
    def visit(self, visitor, *args):
        func = getattr(visitor, f'visit_{ type(self).__name__.lower() }')
        return func(self, *args)

    def __str__(self):
        return type(self).__name__


class String(Type):
    pass


class Integer(Type):
    pass


class Boolean(Type):
    pass


class Null(Type):
    pass


class Object(Type):
    def __init__(self, fields):
        self.optional_keys = frozenset(key for key, value
                                in fields.items()
                                if isinstance(value, Optional))

        self.fields = {key: value.type if isinstance(value, Optional) else value
                        for key, value in fields.items()}


class Optional:
    """ This is NOT a type
    """
    def __init__(self, type_):
        self.type = type_


class List(Type):
    def __init__(self, type_):
        self.type = type_


class Any(Type):
    pass


class Const(Type):
    def __init__(self, value):
        self.value = value


class Reference(Type):
    def __init__(self, name):
        self.name = name


class OneOf(Type):
    def __init__(self, *types):
        self.types = types


class Unset(Type):
    class UNSET:
        pass
