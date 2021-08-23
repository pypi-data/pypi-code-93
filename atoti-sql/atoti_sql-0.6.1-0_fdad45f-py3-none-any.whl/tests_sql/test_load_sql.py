from pathlib import Path
from typing import Any, Mapping, Optional

import pytest

import atoti as tt
from atoti._plugins import MissingPluginError
from atoti.session import Session

DATABASE_PATH = Path(__file__).parent / "resources" / "h2database"
H2_USERNAME = "root"
H2_PASSWORD = ""
DATABASE_URL = (
    f"h2:{str(DATABASE_PATH.absolute())};USER={H2_USERNAME};PASSWORD={H2_PASSWORD}"
)

TYPES = {
    "ID": tt.type.INT,
    "CITY": tt.type.STRING,
    "MY_VALUE": tt.type.NULLABLE_DOUBLE,
}
SQL_QUERY = "SELECT * FROM MYTABLE;"


@pytest.mark.sql
def test_load_sql_h2_database(session: Session):
    table = session.create_table("test sql", types=TYPES, keys=["ID"])
    assert len(table) == 0
    table.load_sql(SQL_QUERY, url=DATABASE_URL)
    assert len(table) == 5


@pytest.mark.sql
def test_read_sql_h2_database(session: Session):
    table = session.read_sql(
        SQL_QUERY,
        url=DATABASE_URL,
        table_name="sql",
        keys=["ID"],
    )
    assert len(table) == 5
    assert table.columns == ["ID", "CITY", "MY_VALUE"]
    assert table._types == TYPES


@pytest.mark.sql
@pytest.mark.parametrize(
    "types", [None, {"MY_VALUE": {"java_type": "double", "nullable": False}}]
)
def test_read_sql_h2_database_with_types(
    session: Session, types: Optional[Mapping[str, Any]]
):
    table = session.read_sql(
        SQL_QUERY,
        url=DATABASE_URL,
        table_name="SQL table",
        keys=["ID"],
        types={
            column_name: tt.type.DataType(**kwargs)
            for column_name, kwargs in types.items()
        }
        if types
        else None,
    )
    assert len(table) == 5
    assert table.columns == ["ID", "CITY", "MY_VALUE"]
    assert (
        table._types["MY_VALUE"] == tt.type.DataType(**types["MY_VALUE"])
        if types
        else tt.type.NULLABLE_FLOAT
    )


def test_missing_plugin_load_sql(session: Session):
    table = session.create_table("test sql", types=TYPES, keys=["ID"])
    with pytest.raises(MissingPluginError):
        table.load_sql(SQL_QUERY, url=DATABASE_URL)


def test_missing_plugin_create_sql(session: Session):
    with pytest.raises(MissingPluginError):
        session.read_sql(
            SQL_QUERY,
            url=DATABASE_URL,
            table_name="sql",
        )
