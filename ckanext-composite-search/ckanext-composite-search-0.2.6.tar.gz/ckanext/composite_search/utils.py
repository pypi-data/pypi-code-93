import ckan.plugins.toolkit as tk

def identity(v):
    return v


def try_bool(v):
    try:
        return tk.asbool(v)
    except ValueError:
        return bool(v)


class SearchParam:
    keys = ("value", "type", "junction", "negation")
    converters = (identity, identity, identity, try_bool)
    value: str
    type: str
    junction: str
    negation: bool

    def __init__(self, *values):
        for k, v, conv in zip(self.keys, values, self.converters):
            setattr(self, k, conv(v))

    def __repr__(self):
        return f'SearchParam({self.value!r}, {self.type!r}, {self.junction!r}, {self.negation!r})'

    def __bool__(self):
        return bool(self.value)
