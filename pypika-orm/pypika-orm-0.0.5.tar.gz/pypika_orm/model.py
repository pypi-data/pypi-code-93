import typing as t

from pypika.queries import Table, Selectable

#  from .types import SQLType, MAP_PYTYPES
from .fields import Field


class ModelOptions:
    """Prepare options for an model."""

    table_name: str = ''
    primary_key: t.Optional[t.Sequence[str]] = None

    def __init__(self, cls):
        """Inherit meta options."""
        for base in reversed(cls.mro()):
            if hasattr(base, "Meta"):
                for k, v in base.Meta.__dict__.items():
                    if not k.startswith('_'):
                        setattr(self, k, v)

        self.setup(cls)

    def setup(self, cls):
        """Setup the options."""
        cls.meta = self

        self.table_name = self.table_name or cls.__name__.lower()
        self.table = Table(self.table_name)  # TODO: do we need it?
        self.primary_key = None

        self.fields = {}
        for name in vars(cls):
            attr = getattr(cls, name)
            if isinstance(attr, Field):
                attr.bind(cls, name)
                self.primary_key = self.primary_key or (name,)


class Model(Selectable):
    """Base model class."""

    def __init__(self, **kwargs):
        """Initialize the model."""
        for name, field in self.meta.fields.items():
            value = kwargs.get(name, None if field.default is None else field.default)
            setattr(self, name, value)

    def __init_subclass__(cls, **kwargs):
        ModelOptions(cls)
        return cls

    @classmethod
    def get_sql(cls, **kwargs: t.Any) -> str:
        return cls.meta.table.get_sql(**kwargs)
