"""awswrangler catalog utilities."""
from typing import Any

import awswrangler as wr
import pandas as pd


def get_schema_df(**kwargs: Any) -> pd.DataFrame:
    """Return a Pandas dataframe having the combined schema of each of the tables in the AWS Catalog.

    The returned dataframe has the columns: Database, Table, Column Name, Type, Partition, Comment

    :param kwargs: These are forwarded to `awswrangler.catalog.tables` for filtering the tables.
                   The `catalog_id` and `boto3_session` args are also forwarded to awswrangler.catalog.table.

    Example:
    -------
        df = get_schema_df(database="my_db", name_prefix="my_tables_")

    """
    # Ref: https://aws-data-wrangler.readthedocs.io/en/stable/stubs/awswrangler.catalog.tables.html#awswrangler.catalog.tables
    def get_table_df(database: str, table: str) -> pd.DataFrame:
        df_table = wr.catalog.table(database=database, table=table, catalog_id=kwargs.get("catalog_id"), boto3_session=kwargs.get("boto3_session"))
        assert all(c not in df_table.columns for c in ("Database", "Table"))
        df_table.insert(0, "Database", database)
        df_table.insert(1, "Table", table)
        return df_table

    return pd.concat([get_table_df(t.Database, t.Table) for t in wr.catalog.tables(**kwargs).itertuples()], ignore_index=True)
