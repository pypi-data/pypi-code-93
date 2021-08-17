from pandas.core.frame import DataFrame
import pytest
import numpy as np
import pandas as pd
from cannerflow.client import Client
from cannerflow.dto import SqlQueryStatus
from cannerflow.query import Query as CannerflowQuery


def test_list_saved_query(cannerflow_client: Client):

    saved_query = cannerflow_client.list_saved_query()
    assert isinstance(saved_query, list), "should get a list"


def test_use_saved_query(cannerflow_client: Client):
    saved_query = cannerflow_client.list_saved_query()
    if len(saved_query) is 0:
        return
    query = cannerflow_client.use_saved_query(saved_query[0])
    query.wait_for_finish(timeout=300)
    print(query)
    assert isinstance(query, CannerflowQuery), "should get a query instance"
    assert type(query.id) == str, "query id should be a string"
    assert isinstance(query.status, SqlQueryStatus), "query status should a string"
    assert type(query.row_count) == int, "query row_count should be a int"
    assert type(query.statement_id) == str, "query statement_id should a string"

    assert isinstance(
        query.columns, list
    ), "columns should be list, but got {columns}".format(columns=query.columns)

    first = query.get_first()
    assert len(first) == 2, "should only get 2 (includes one column row)"

    all_data = query.get_all()
    assert (
        len(all_data) == query.row_count + 1
    ), "should get row_count + 1 (includes the column)"

    any_data = query.get(10, 3)
    assert len(any_data) <= 11, "should get less than 11 rows (includes the column)"

    query.data_format = "df"
    first = query.get_first()
    assert isinstance(first, pd.DataFrame), "should be a dataframe"

    query.data_format = "np"
    first = query.get_first()
    assert isinstance(first, np.ndarray), "should be a np array"


def test_gen_query_with_row_data(cannerflow_client: Client):
    query = cannerflow_client.gen_query(
        "SELECT CAST(ROW(ARRAY[1], 2.0) AS ROW(x ARRAY(BIGINT), y DOUBLE))",
        cache_refresh=True,
    )
    query.wait_for_finish(timeout=300)
    assert query.status == SqlQueryStatus.FINISHED, "status must be finished"
    assert query.row_count == 1, "should have row_count"
    assert len(query.get_first(1)) == 2, "should get two columns"


def test_gen_query_with_empty_data(cannerflow_client: Client):
    query = cannerflow_client.gen_query(
        "select * from tpch.tiny.lineitem limit 0", cache_refresh=True
    )
    query.wait_for_finish(timeout=300)
    assert query.status == SqlQueryStatus.FINISHED, "status must be finished"
    assert query.row_count == 0, "should have row_count"
    assert len(query.get_first(1)) == 1, "should only get column"


def test_gen_query_with_empty_data_in_df(cannerflow_client: Client):
    query = cannerflow_client.gen_query(
        "select * from tpch.tiny.lineitem limit 0", cache_refresh=True, data_format="df"
    )
    query.wait_for_finish(timeout=300)
    assert query.status == SqlQueryStatus.FINISHED, "status must be finished"
    assert query.row_count == 0, "should have row_count"
    df = query.get_all()

    column_results = DataFrame(df).columns.tolist()
    assert len(column_results) != 0, "should get columns in data frame"


def test_gen_query(cannerflow_client: Client):
    query = cannerflow_client.gen_query(
        "select * from tpch.tiny.lineitem limit 1000", cache_refresh=True
    )
    query.wait_for_finish(timeout=300)
    assert query.status == SqlQueryStatus.FINISHED, "status must be finished"
    assert query.row_count > 0, "should have row_count"
    assert len(query.get_first(1)) == 2, "should get 2 rows include column"


def test_get_data_flow(cannerflow_client: Client):
    query = cannerflow_client.gen_query(
        """ SELECT * FROM (
        VALUES (1, 10), (2, 20), (3, 30), (4, 40), (5, 50), (6, 60), (7, 70), (8, 80), (9, 90), (10, 100)
    ) AS testtable(col, col10)
    """
    )
    query.wait_for_finish(timeout=5, period=3)
    data = list(query.get_all())
    assert data[0] == ["col", "col10"]
    data = data[1:11]  # remove header
    assert len(data) is 10

    first3 = query.get_first(limit=3)
    first3 = first3[1:4]  # remove header
    assert len(first3) is 3
    assert first3 == data[0:3]

    last3 = query.get_last(limit=3)
    last3 = last3[1:4]  # remove header
    assert len(last3) is 3
    assert last3 == data[7:10]

    middle = query.get(limit=3, offset=3)
    middle = middle[1:4]  # remove header
    assert len(middle) is 3
    assert middle == data[3:6]


def test_show_nested_warning(cannerflow_client: Client, caplog):
    nestedsql = """SELECT * FROM (
        VALUES (
            ARRAY[CAST(ROW(1, 2.0) AS ROW(x BIGINT, y DOUBLE)), CAST(ROW(2, 4.0) AS ROW(x BIGINT, y DOUBLE))],
            MAP(ARRAY['1', '2'], ARRAY[CAST(ROW(1, 2.0) AS ROW(x BIGINT, y DOUBLE)), CAST(ROW(2, 4.0) AS ROW(x BIGINT, y DOUBLE))]),
            CAST(ROW(1, CAST(ROW(1, 2.0) AS ROW(x BIGINT, y DOUBLE))) AS ROW(x BIGINT, y ROW(x BIGINT, y DOUBLE)))
        )
    ) AS nestedtable (array_of_row, map_of_row, row_of_row)"""

    query = cannerflow_client.gen_query(nestedsql, data_format="df", fetch_by="storage")
    query.wait_for_finish(timeout=300)
    df = query.get_all()
    assert (
        len(caplog.messages) is 3
    ), f"Expect that got 3 warnings but {len(caplog.messages)}."
    assert caplog.messages[0].find(
        "array_of_row"
    ), "Didn't get the warning for array_of_row column."
    assert caplog.messages[1].find(
        "map_of_row"
    ), "Didn't get the warning for map_of_row column."
    assert caplog.messages[2].find(
        "row_of_row"
    ), "Didn't get the warning for row_of_row column."


@pytest.mark.parametrize(
    "input_sql_query,expected",
    [
        (
            "test",
            "line 1:1: mismatched input 'test'. Expecting: 'ALTER', 'ANALYZE', 'CALL', 'COMMENT', 'COMMIT', 'CREATE', 'DEALLOCATE', 'DELETE', 'DESC', 'DESCRIBE', 'DROP', 'EXECUTE', 'EXPLAIN', 'GRANT', 'INSERT', 'PREPARE', 'RESET', 'REVOKE', 'ROLLBACK', 'SET', 'SHOW', 'START', 'USE', <query>",
        ),
        (
            "slect * from tpch.tiny.lineitem limit 1",
            "line 1:1: mismatched input 'slect'. Expecting: 'ALTER', 'ANALYZE', 'CALL', 'COMMENT', 'COMMIT', 'CREATE', 'DEALLOCATE', 'DELETE', 'DESC', 'DESCRIBE', 'DROP', 'EXECUTE', 'EXPLAIN', 'GRANT', 'INSERT', 'PREPARE', 'RESET', 'REVOKE', 'ROLLBACK', 'SET', 'SHOW', 'START', 'USE', <query>",
        ),
        (
            "select from tpch.tiny.lineitem limit 1",
            "line 1:8: mismatched input 'from'. Expecting: '*', 'ALL', 'DISTINCT', <expression>",
        ),
        ("select * from tpch.tiny limit 1", "line 2:15: Schema 'tpch' does not exist"),
        ("select *", "line 2:8: SELECT * not allowed in queries without FROM clause"),
        ("select 0 from tpch.tiny limit 1", "line 2:15: Schema 'tpch' does not exist"),
        (
            "select -",
            "line 1:9: mismatched input '<EOF>'. Expecting: <expression>, <integer>, DECIMAL_VALUE, DOUBLE_VALUE",
        ),
    ],
)
def test_should_throw_sql_failed_when_query_with_error_sql_syntax(
    cannerflow_client: Client, input_sql_query: str, expected: str
):
    # Arrange

    # Act
    with pytest.raises(Exception) as excinfo:
        cannerflow_client.gen_query(input_sql_query, cache_refresh=True)

    # Assert
    assert (
        str(excinfo.value.args[1]) == expected
    ), f"should be throw error with message {expected}"


class TestQueryWithIterator(object):
    def test_should_count_correct_when_query_large_data_with_loop(
        self,
        cannerflow_client: Client,
    ):
        expected = 37435
        sql_sql = f"select * from tpch.tiny.lineitem limit {expected}"
        query = cannerflow_client.gen_query(sql_sql, cache_refresh=True)
        query.wait_for_finish(timeout=300)

        assert query.status == SqlQueryStatus.FINISHED, "status must be finished"
        assert query.row_count > 0, "should have row_count"
        count = 0
        for row in query:
            assert len(row) == 2, "should format as [columns, data]"
            count += 1
        # Assert
        assert count == expected, f"should get {expected} lines"

    def test_should_count_correct_when_query_large_data_with_list_comprehension(
        self,
        cannerflow_client: Client,
    ):
        expected = 37435
        sql_sql = f"select * from tpch.tiny.lineitem limit {expected}"
        query = cannerflow_client.gen_query(sql_sql, cache_refresh=True)
        query.wait_for_finish(timeout=300)

        assert query.status == SqlQueryStatus.FINISHED, "status must be finished"
        assert query.row_count > 0, "should have row_count"
        count = len([row for row in query])
        # Assert
        assert count == expected, f"should get {expected} lines"

    def test_should_count_correct_when_query_small_data_with_loop(
        self,
        cannerflow_client: Client,
    ):
        expected = 100
        sql_sql = f"select * from tpch.tiny.lineitem limit {expected}"
        query = cannerflow_client.gen_query(sql_sql, cache_refresh=True)
        query.wait_for_finish(timeout=300)

        assert query.status == SqlQueryStatus.FINISHED, "status must be finished"
        assert query.row_count > 0, "should have row_count"
        count = 0
        for row in query:
            assert len(row) == 2, "should format as [columns, data]"
            count += 1
        # Assert
        assert count == expected, f"should get {expected} lines"

    def test_should_count_correct_when_query_small_data_with_list_comprehension(
        self,
        cannerflow_client: Client,
    ):
        expected = 100
        sql_sql = f"select * from tpch.tiny.lineitem limit {expected}"
        query = cannerflow_client.gen_query(sql_sql, cache_refresh=True)
        query.wait_for_finish(timeout=300)

        assert query.status == SqlQueryStatus.FINISHED, "status must be finished"
        assert query.row_count > 0, "should have row_count"
        count = len([row for row in query])
        # Assert
        assert count == expected, f"should get {expected} lines"

    def test_should_all_df_when_query_with_df_format(self, cannerflow_client: Client):
        # Arrange
        sql_query = "select * from tpch.tiny.lineitem limit 100"
        query = cannerflow_client.gen_query(
            sql_query,
            cache_refresh=True,
            data_format="df",
        )
        query.wait_for_finish(timeout=300)

        # Act
        is_all_dataframe = [isinstance(row, pd.DataFrame) for row in query]

        # Assert
        assert all(is_all_dataframe) == True, "should be format as data frame"
