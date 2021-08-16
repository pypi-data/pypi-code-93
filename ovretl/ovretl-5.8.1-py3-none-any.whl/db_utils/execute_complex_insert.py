import psycopg2
import pandas as pd
from ovretl.db_utils.fetch_db_credentials import fetch_db_credentials


def execute_complex_insert(df: pd.DataFrame, stage="dev"):
    values_to_insert = [tuple(x) for x in df.values]
    columns = ",".join(df.columns)
    credentials = fetch_db_credentials(stage)
    conn = psycopg2.connect(
        host=credentials["host"],
        user=credentials["username"],
        password=credentials["password"],
        dbname="Rates",
        port=6543,
    )
    cur = conn.cursor()
    from psycopg2.extras import execute_values

    execute_values(
        cur,
        """INSERT INTO "RateMeta" (
                  {}
                  ) VALUES %s ON CONFLICT ON CONSTRAINT {}
                  DO UPDATE SET
                  "updated_at" = NOW(),
                  "margin_type" = EXCLUDED."margin_type",
                  "margin_value" = EXCLUDED."margin_value"
                   """.format(
            columns, "unicity_on_kronos_name"
        ),
        values_to_insert,
    )
    cur.close()
    conn.commit()
    conn.close()
    print("Inserted {} rows.".format(cur.rowcount))
