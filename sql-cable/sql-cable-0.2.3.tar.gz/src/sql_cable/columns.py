
class Set_Null:
    def __init__(self):
        self.sql = "SET NULL"


class Set_Default:
    def __init__(self):
        self.sql = "SET DEFAULT"


class Cascade:
    def __init__(self):
        self.sql = "CASCADE"


def type_to_sql_type(type):
    if type == float:
        sql_type = "REAL"
    elif type == int:
        sql_type = "INTEGER"
    elif type == str:
        sql_type = "STRING"
    elif type == bool:
        sql_type = "BOOLEAN"
    return sql_type


def sql_args(column):
    args_str = ""
    if column.unique:
        args_str += " UNIQUE"
    if column.not_null:
        args_str += " NOT NULL"
    if column.default:
        if type(column.default) == str:
            args_str += f" DEFAULT [{column.default}]"
        else:
            args_str += f" DEFAULT {column.default}"
    return args_str


def lenght_sql(column):
    lenght_str = ""
    if column.max_length and not column.min_length:
        lenght_str += f" ({column.max_length})"
    if column.min_length and column.min_length:
        lenght_str += f"({column.min_length}, {column.max_length})"
    return lenght_str


class PrimaryKeyColumn:
    def __init__(self, autoincrement=False, type=int):
        self.name = None
        self.pk = True
        self.autoincrement = autoincrement
        self.fk = False
        self.type = type_to_sql_type(type)
        self.unique = False
        self.not_null = False
        self.default = None

    def generate_sql(self):
        return f"{self.name} {self.type} PRIMARY KEY{' AUTOINCREMENT' if self.autoincrement else ''}"


class ForeignKeyColumn:
    def __init__(self, foreign_model, type=int, on_delete=Cascade(), unique=False, not_null=False, default=None):
        self.name = None
        self.pk = False
        self.fk = True
        self.type = type_to_sql_type(type)
        self.foreign_model = foreign_model
        self.on_delete = on_delete
        self.unique = unique
        self.not_null = not_null
        self.default = default

    def generate_sql(self):
        self.foreign_model.get_column(self.foreign_model)
        return f"{self.name} {self.type}{sql_args(self)} REFERENCES {self.foreign_model.model.name} ({self.foreign_model.primary_key(self.foreign_model)})  ON DELETE {self.on_delete.sql}"


class IntegerColumn:
    def __init__(self, unique=False, not_null=False, default=None, max_length=None, min_length=None):
        self.name = None
        self.pk = False
        self.fk = False
        self.max_length = max_length
        self.min_length = min_length
        self.type = type_to_sql_type(int) + lenght_sql(self)
        self.unique = unique
        self.not_null = not_null
        self.default = default

    def generate_sql(self):
        return f"{self.name} {self.type}{sql_args(self)}"


class StringColumn:
    def __init__(self, unique=False, not_null=False, default=None, max_length=None, min_length=None):
        self.name = None
        self.pk = False
        self.fk = False
        self.max_length = max_length
        self.min_length = min_length
        self.type = type_to_sql_type(str) + lenght_sql(self)
        self.max_length = max_length
        self.min_length = min_length
        self.unique = unique
        self.not_null = not_null
        self.default = default

    def generate_sql(self):
        return f"{self.name} {self.type}{sql_args(self)}"


class FloatColumn:
    def __init__(self, unique=False, not_null=False, default=None, max_length=None, min_length=None):
        self.name = None
        self.pk = False
        self.fk = False
        self.max_length = max_length
        self.min_length = min_length
        self.type = type_to_sql_type(float) + lenght_sql(self)
        self.unique = unique
        self.not_null = not_null
        self.default = default

    def generate_sql(self):
        return f"{self.name} {self.type}{sql_args(self)}"


class BooleanColumn:
    def __init__(self, unique=False, not_null=False, default=None):
        self.name = None
        self.pk = False
        self.fk = False
        self.type = type_to_sql_type(bool)
        self.unique = unique
        self.not_null = not_null
        self.default = default

    def generate_sql(self):
        return f"{self.name} {self.type}{sql_args(self)}"
