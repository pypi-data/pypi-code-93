import psycopg2

from ovretl.db_utils.fetch_db_credentials import fetch_db_credentials


def execute_simple_query(query: str, dbname: str, stage="dev", select=False):
    result = None
    credentials = fetch_db_credentials(stage=stage)
    conn = psycopg2.connect(
        host=credentials["host"],
        user=credentials["username"],
        password=credentials["password"],
        dbname=dbname,
        port=6543,
    )
    cur = conn.cursor()
    cur.execute(query)
    return cur.description
    if select:
        result = cur.fetchall()
    cur.close()
    conn.commit()
    conn.close()
    return result
