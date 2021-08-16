from typing import List

import psycopg2

from ovretl.db_utils.fetch_db_credentials import fetch_db_credentials


def execute_complexe_update_three_cols(
    set_column: str,
    set_data: List,
    where_column_1: str,
    where_data_1: List,
    where_column_2: str,
    where_data_2: List,
    table_name: str,
    dbname: str,
    stage="dev",
):
    """
    Update table in DB with 3 vectors, one to set, 2 to know where.
    :param set_column: Name of the column to update
    :param set_data: New data
    :param where_column: Name of the column to lookup
    :param where_data: Data to lookup
    :param table_name: table name
    :param dbname: database name
    :param stage: dev or prod
    :return: void
    """
    assert len(set_data) == len(where_data_1) == len(where_data_2)
    values_to_insert = list(zip(set_data, where_data_1, where_data_2))
    credentials = fetch_db_credentials(stage)
    conn = psycopg2.connect(
        host=credentials["host"],
        user=credentials["username"],
        password=credentials["password"],
        dbname=dbname,
        port=6543,
    )
    cur = conn.cursor()
    from psycopg2.extras import execute_values

    execute_values(
        cur,
        """UPDATE "{0}" SET "{1}" = data."{1}" FROM (VALUES %s) AS data ({1}, {2}, {3}) WHERE "{0}".{2} = data.{2} AND "{0}".{3} = data.{3} """.format(
            table_name, set_column, where_column_1, where_column_2
        ),
        values_to_insert,
    )

    print("Updated {} rows".format(cur.rowcount))
    cur.close()
    conn.commit()
    conn.close()
