import abc
import dataclasses
import difflib
import typing
from operator import attrgetter

import yaml

# A registry of output types so they can be found by name
OUTPUT_TYPES = {}


@dataclasses.dataclass
class Output(abc.ABC):
    """
    An artifact produced by the transform, ie a table or file etc. Defining outputs serves two
    purposes: we can run validations against them after the transform runs and we can create the
    artifact as an input to a downstream transform when running tests.
    """

    name: str

    def __init_subclass__(cls, **kwargs):
        """Register subclasses so they can be found by name"""
        assert cls not in OUTPUT_TYPES, f"Attempted to register {cls.__name__} twice"
        OUTPUT_TYPES[cls.__name__] = cls
        super().__init_subclass__(**kwargs)

    @abc.abstractmethod
    def test_setup(self, context: dict, values: list = None):
        """Create a stub of the artifact, ie create the table"""

    @abc.abstractmethod
    def test_results(self, context: dict) -> list:
        """Get the artifact value, ie rows"""

    @abc.abstractmethod
    def validate(self, context: dict):
        """Check the output after running the transform"""


@dataclasses.dataclass
class Column:
    """A database table column"""

    name: str
    datatype: str
    nullable: bool = dataclasses.field(default=False)

    def __post_init__(self):
        # map pseudo-types back to the type found in information_schema
        self.datatype = {"serial": "integer", "bigserial": "bigint"}.get(
            self.datatype, self.datatype
        )

    @property
    def null(self):
        return "NULL" if self.nullable else "NOT NULL"


class BaseSql(Output, abc.ABC):
    """Common Sql functionality"""

    def validate(self, context):
        """Run validation queries and check that the schema matches"""
        self._validate_schema(context)
        self._validation_queries(context)

    @staticmethod
    def _get_columns(context, name, source="information_schema.columns"):
        sql = (
            f"SELECT column_name, data_type, is_nullable = 'YES' "
            f"FROM {source} WHERE table_name = '{name}'"
            f"ORDER BY ordinal_position"
        )
        cursor = context["conn"].cursor()
        cursor.execute(sql)
        return [Column(*col) for col in cursor.fetchall()]

    @staticmethod
    def _diff_columns(actual, expected):
        """Dump columns to YAML for human-readable assertion output"""
        actual = str(yaml.safe_dump([dataclasses.asdict(col) for col in actual])).splitlines()
        expected = str(yaml.safe_dump([dataclasses.asdict(col) for col in expected])).splitlines()
        if actual != expected:
            result = "\n".join(difflib.Differ().compare(actual, expected))
            raise AssertionError(f"Columns do not match. Difference is:\n{result}")

    @abc.abstractmethod
    def _validate_schema(self, context):
        """Check that the columns match the expected schema"""

    def _validation_queries(self, context):
        """
        Run each user provided validation query. If there are any rows returned,
        report a failure.
        """
        cursor = context["conn"].cursor()
        errors = []
        for query in self.validation_queries:
            cursor.execute(query)
            if cursor.rowcount > 0:
                errors.append(
                    f"Failed {cursor.rowcount} times, first value is {cursor.fetchone()[0]}"
                )
        assert not errors, "Validation queries failed"


@dataclasses.dataclass
class Table(BaseSql):
    """A database table"""

    columns: typing.List
    validation_queries: typing.List[str] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        self.columns = [Column(**col) for col in self.columns]

    def test_setup(self, context: dict, values: typing.List[dict] = None):
        """Create the table for use in tests. If initial values are provided, insert them."""
        columns = [f"{col.name} {col.datatype} {col.null}" for col in self.columns]
        sql = f"CREATE TABLE {self.name} ({', '.join(columns)})"
        cursor = context["conn"].cursor()
        cursor.execute(sql)
        if values:
            # values is a list of dicts to be inserted as rows
            columns = ", ".join(values[0].keys())
            placeholders = ", ".join(["%s"] * len(values[0]))
            placeholders = ", ".join([f"({placeholders})"] * len(values))
            values = [val for row in values for val in row.values()]
            cursor.execute(f"INSERT INTO {self.name} ({columns}) VALUES {placeholders}", values)

    def test_results(self, context: dict):
        cursor = context["conn"].cursor()
        cursor.execute(f"SELECT * FROM {self.name}")
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def _validate_schema(self, context):
        db_columns = self._get_columns(context, self.name)
        self._diff_columns(db_columns, self.columns)


@dataclasses.dataclass
class DjangoTable(BaseSql):
    """A database table defined using Django"""

    validation_queries: typing.List[str] = dataclasses.field(default_factory=list)

    def test_setup(self, context: dict, values: list = None):
        """Tables are created by Django migrations so nothing needed here"""

    def test_results(self, context: dict) -> list:
        """Use `Model.objects.all()` instead to get rows"""

    def _validate_schema(self, context):
        from django.apps import apps
        from django.db import connection

        model = apps.get_model(self.name)
        db_columns = self._get_columns(context, model._meta.db_table)
        model_columns = [
            Column(field.column, field.db_type(connection), field.null)
            for field in model._meta.get_fields()
            # ignore fields which are not DB columns:
            if not field.many_to_many and not field.one_to_many
        ]
        model_columns.sort(key=attrgetter("name"))
        db_columns.sort(key=attrgetter("name"))
        self._diff_columns(db_columns, model_columns)


@dataclasses.dataclass
class BigQueryTable(Table):
    """
    A table in BigQuery

    - The table name should include the dataset but the project is optional
    - ``workflows.testing`` does not support BigQuery outputs, because it
      provides a Postgres ``conn``. Since there are no transactions in BigQuery
      it's not clear how testing should be supported, because test runs could
      interfere with each other or overwrite production data.
    """

    def _validate_schema(self, context):
        name_parts = self.name.split(".")
        table = name_parts[-1]
        source = f"{'.'.join(name_parts[:-1])}.INFORMATION_SCHEMA.COLUMNS"
        db_columns = self._get_columns(context, table, source)
        self._diff_columns(db_columns, self.columns)
