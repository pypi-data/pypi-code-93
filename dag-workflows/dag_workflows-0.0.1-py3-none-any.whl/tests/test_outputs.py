import pytest
import yaml
from django.db import connection

from workflows import outputs

TABLE_SPEC = """
name: test_table
columns:
- name: column1
  datatype: text
- name: column2
  datatype: integer
  nullable: true
validation_queries:
- |
  select * from test_table
"""


def get_table():
    spec = yaml.safe_load(TABLE_SPEC)
    return outputs.Table(**spec), {"conn": connection}


@pytest.mark.django_db
def test_table_output_setup():
    table, context = get_table()
    table.test_setup(context)
    table._validate_schema(context)


@pytest.mark.django_db
def test_table_output_schema_fail():
    table, context = get_table()

    # don't create the table, therefore there are no columns
    with pytest.raises(AssertionError, match="Columns do not match"):
        table._validate_schema(context)


@pytest.mark.django_db
def test_table_output_validation_queries():
    table, context = get_table()
    table.test_setup(context)

    # table is empty - validation passes
    table.validate(context)

    # table has a row - validation fails
    connection.cursor().execute("INSERT INTO test_table VALUES ('hello', 1)")
    with pytest.raises(AssertionError, match="Validation queries failed"):
        table.validate(context)


DJANGO_SPEC = """
name: example_project.Person
"""


@pytest.mark.django_db
def test_django_output_schema():
    spec = yaml.safe_load(DJANGO_SPEC)
    table = outputs.DjangoTable(**spec)
    table._validate_schema({"conn": connection})


def test_bigquery_output_schema(mocker):
    mock = mocker.patch("workflows.outputs.BaseSql._get_columns", autospec=True)
    spec = yaml.safe_load(TABLE_SPEC)
    spec["name"] = "project.dataset.table"
    mock.return_value = [outputs.Column(**col) for col in spec["columns"]]
    table = outputs.BigQueryTable(**spec)
    table._validate_schema(None)

    mock.assert_called_once_with(None, "table", "project.dataset.INFORMATION_SCHEMA.COLUMNS")
