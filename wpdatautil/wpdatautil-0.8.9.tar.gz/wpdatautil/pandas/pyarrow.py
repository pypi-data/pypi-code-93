"""pandas pyarrow utilities."""
import pandas as pd
import pyarrow.parquet
import smart_open


def read_parquet_schema_df(uri: str) -> pd.DataFrame:
    """Return a Pandas dataframe corresponding to the schema of a local or S3 URI of a parquet file.

    The returned dataframe has the columns: column, pa_dtype
    """
    # Ref: https://stackoverflow.com/a/64288036/
    with smart_open.open(uri, "rb") as parquet_file:
        schema = pyarrow.parquet.read_schema(parquet_file, memory_map=True)
    schema = pd.DataFrame(({"column": name, "pa_dtype": str(pa_dtype)} for name, pa_dtype in zip(schema.names, schema.types)))
    schema = schema.reindex(columns=["column", "pa_dtype"], fill_value=pd.NA)  # Ensures columns in case the parquet file has an empty dataframe.
    return schema
