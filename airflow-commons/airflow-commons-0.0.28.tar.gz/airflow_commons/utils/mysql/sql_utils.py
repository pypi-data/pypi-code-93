from airflow_commons.utils.file_utils import read_sql
from airflow_commons.sql_resources.mysql import DELETE_SQL_FILE
from airflow_commons.sql_resources.mysql import SELECT_ALL_SQL_FILE


def get_delete_sql(
    table_name: str,
    where_statement: str,
):
    """
    Returns a delete dml query

    :param table_name: table name
    :param where_statement: delete condition
    :return: sql statement as a string
    """
    return read_sql(
        sql_file=DELETE_SQL_FILE,
        table_name=table_name,
        where_statement=where_statement,
    )


def get_select_all_sql(
    table_name: str,
    where_statement: str,
):
    """
    Returns a select sql query

    :param table_name: table name
    :param where_statement: select condition
    :return: sql statement as a string
    """
    return read_sql(
        sql_file=SELECT_ALL_SQL_FILE,
        table_name=table_name,
        where_statement=where_statement,
    )
