from typing import List

import psycopg2

from ovretl.db_utils.fetch_db_credentials import fetch_db_credentials


def execute_complexe_update(
    set_column: str, set_data: List, where_column: str, where_data: List, table_name: str, dbname: str, stage="dev",
):
    """
    Update table in DB with 2 vectors, one to set, one to know where.
    :param set_column: Name of the column to update
    :param set_data: New data
    :param where_column: Name of the column to lookup
    :param where_data: Data to lookup
    :param table_name: table name
    :param dbname: database name
    :param stage: dev or prod
    :return: void
    """
    assert len(set_data) == len(where_data)
    values_to_insert = list(zip(set_data, where_data))
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

    if set_column != where_column:
        execute_values(
            cur,
            """UPDATE "{0}" SET "{1}" = data."{1}" FROM (VALUES %s) AS data ({1}, {2}) WHERE "{0}".{2} = data.{2}""".format(
                table_name, set_column, where_column
            ),
            values_to_insert,
        )
    else:
        execute_values(
            cur,
            """UPDATE "{0}" SET "{1}" = data."{1}" FROM (VALUES %s) AS data ({1}, {1}_old) WHERE "{0}".{1} = data.{1}_old""".format(
                table_name, set_column
            ),
            values_to_insert,
        )
    print("Updated {} rows".format(cur.rowcount))
    cur.close()
    conn.commit()
    conn.close()
