import psycopg2

from ovretl.db_utils.fetch_db_credentials import fetch_db_credentials


def execute_simple_update(
    set_column: str, set_value, where_column: str, where_value, table_name: str, dbname: str, stage="dev",
):
    credentials = fetch_db_credentials(stage)
    conn = psycopg2.connect(
        host=credentials["host"],
        user=credentials["username"],
        password=credentials["password"],
        dbname=dbname,
        port=6543,
    )
    cur = conn.cursor()
    query = """UPDATE "{0}" SET "{1}" = %s WHERE "{2}" = CAST(%s as character varying [])""".format(
        table_name, set_column, where_column
    )
    cur.execute(query, (set_value, where_value))
    print(cur.query)
    print("Updated {} rows".format(cur.rowcount))
    cur.close()
    conn.commit()
    conn.close()
