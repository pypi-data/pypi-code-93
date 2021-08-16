import psycopg2
import pandas as pd
from ovretl.db_utils.fetch_db_credentials import fetch_db_credentials


def execute_simple_insert(df: pd.DataFrame, table_name: str, dbname: str, stage="dev"):
    values_to_insert = [tuple(x) for x in df.values]
    columns = '"{}"'.format('","'.join(df.columns))
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
        """INSERT INTO "{}" (
                  {}
                  ) VALUES %s""".format(
            table_name, columns
        ),
        values_to_insert,
    )
    cur.close()
    conn.commit()
    conn.close()
    print("Inserted {} rows.".format(cur.rowcount))
