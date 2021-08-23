import typing as t

import datetime
import decimal

from pypika.queries import Field as _Field, builder


if t.TYPE_CHECKING:
    from .model import Model


class FieldMeta(type):

    py_type: t.Type

    def __new__(mcs, name: str, bases: t.Tuple[t.Type, ...], attrs: dict):
        if len(bases) > 1 and issubclass(bases[0], Field):
            base, *types = bases
            attrs['py_type'] = types[0] if len(types) == 1 else t.Union[types]
            cls = super(FieldMeta, mcs).__new__(mcs, name, (base,), attrs)
            return cls

        return super(FieldMeta, mcs).__new__(mcs, name, bases, attrs)


class Field(_Field, metaclass=FieldMeta):

    py_type: t.Type
    db_type: str
    pk: bool = False

    name: str
    model: 'Model'

    def __init__(self, null: bool = None, default: t.Any = None, **meta):
        self.null = null
        self.default = default
        self.meta = meta

    @builder
    def bind(self, model: 'Model', name: str):
        self.name = name
        self.model = model
        self.table = model.meta.table
        model.meta.fields[name] = self
        setattr(model, name, self)
        if self.pk:
            model.meta.pks.append(name)


class BIGINT(Field, int):
    db_type = 'BIGINT'


class BLOB(Field, bytes):
    db_type = 'BLOB'


class BOOL(Field, int):
    db_type = 'SMALLINT'


class CHAR(Field, str):
    db_type = 'CHAR'


class DATE(Field, datetime.date):
    db_type = 'DATE'


class DATETIME(Field, datetime.datetime):
    db_type = 'DATETIME'


class DECIMAL(Field, decimal.Decimal):
    db_type = 'DECIMAL'


class DOUBLE(Field, float):
    db_type = 'REAL'


class FLOAT(Field, float):
    py_type = float


class INTEGER(Field, int):
    db_type = 'INTEGER'


class SMALLINT(Field, int):
    db_type = 'SMALLINT'


class TEXT(Field, str):
    db_type = 'TEXT'


class TIME(Field, datetime.time):
    db_type = 'TIME'


class UUID(Field, str):
    db_type = 'TEXT'


class UUIDB(Field, bytes):
    db_type = 'BLOB'


class VARCHAR(Field, str):

    def __init__(self, max_length: int = 256, **kwargs):
        self.max_length = max_length
        super(VARCHAR, self).__init__(**kwargs)

    @property
    def db_type(self):
        return f"VARCHAR({self.max_length})"
