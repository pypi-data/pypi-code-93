import psycopg2
import pandas as pd

from ovretl.db_utils.fetch_db_credentials import fetch_db_credentials


def select_from_table(entity: str, cluster="dev", schema="public") -> pd.DataFrame:
    """
    dbname is necessary to fetch Rates DB in dev & prod cluster
    :param entity:
    :param cluster: "dev" or "analytics"
    :param after:
    :param schema: "public" default, can be "station" for cluster "analytics"
    :return:
    """
    if cluster == "prod":
        raise ValueError("Cannot query from prod cluster")
    credentials = fetch_db_credentials(cluster=cluster)
    conn = psycopg2.connect(
        host=credentials["host"],
        user=credentials["username"],
        password=credentials["password"],
        dbname=credentials["dbname"],
        port=credentials["port"],
    )
    sql_query = pd.read_sql_query(
        """
    SELECT * FROM "{}"."{}"
    """.format(
            schema, entity
        ),
        conn,
    )

    df = pd.DataFrame(sql_query)
    return df
