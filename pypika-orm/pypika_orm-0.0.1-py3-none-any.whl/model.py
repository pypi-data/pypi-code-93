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

        #  for name, field in inspect.getmembers(cls, lambda m: isinstance(m, Field)):
        #      self.fields[name] = field.bind(cls, name)

            #  # Relation
            #  if hasattr(field, 'model'):
            #      field = ForeignKey(field)
            #      field.model = cls
            #      field.name = name

            #  else:
            #      field.model = cls
            #      field.name = name

            #  self.fields[name] = field

        #  for name, field in inspect.getmembers(cls, lambda m: isinstance(m, Field)):
        #      breakpoint()
        #      pass

        #  for field_name, typehint in t.get_type_hints(cls, include_extras=True).items():
        #      meta = None
        #      self.pks = self.pks or (field_name,)

        #      typehint = MAP_PYTYPES.get(typehint, typehint)
        #      while isinstance(typehint, t._BaseGenericAlias):
        #          typehint, meta = t.get_args(typehint)
        #          typehint = MAP_PYTYPES.get(typehint, typehint)

        #      if isinstance(typehint, ModelField):
        #          column_type = typehint.column_type

        #      elif typehint and issubclass(typehint, SQLType):
        #          column_type = typehint.db_type
        #          if meta:
        #              column_type = f"{column_type}({meta})"

        #      try:
        #          default = getattr(cls, field_name)
        #          nullable = default is None
        #      except AttributeError:
        #          default = nullable = None

        #      field = ModelField(cls, field_name, table=self.table)
        #      setattr(cls, field_name, field)

        #      column = Column(
        #          field_name, column_type=column_type, default=default, nullable=nullable)
        #      self.columns[field_name] = column


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


#  class ModelField(Field):

#      def __init__(self, model: Model, *args, **kwargs):
#          super().__init__(*args, **kwargs)
#          self.model = model

#      @property
#      def column_type(self) -> str:
#          column = self.model.meta.columns[self.name]
#          return column.type
