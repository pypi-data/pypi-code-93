import boto3
import pandas as pd


class Client:
    def __init__(
        self, cluster_id: str, db_name: str = "default_db", username: str = None
    ):
        self.cluster_id = cluster_id
        self.db_name = db_name
        self.username = username or self.get_username_from_sts()
        self.client = boto3.client("redshift-data")

    def get_username_from_sts(self):
        client = boto3.client("sts")
        arn = client.get_caller_identity()["Arn"]
        kind, username = arn.split(":")[-1].split("/")
        if kind != "user":
            raise Exception(
                f"identity of type {kind} not supported, only users allowed"
            )
        return username

    def _parse_cell(self, cell):
        if len(cell) != 1:
            raise Exception(f"invalid cell: {cell}")

        is_null = cell.get("isNull")
        if is_null:
            return None

        (value,) = cell.values()
        return value

    def _parse_row(self, row):
        return (self._parse_cell(cell) for cell in row)

    def execute_query(self, query_string: str):
        query_id = self.client.execute_statement(
            ClusterIdentifier=self.cluster_id,
            Database="default_db",
            DbUser=self.username,
            Sql=query_string,
        )["Id"]
        while True:
            statement = self.client.describe_statement(Id=query_id)
            if statement.get("Error"):
                raise Exception(f"query failed: {statement['Error']}")
            if statement["HasResultSet"]:
                break

        result = self.client.get_statement_result(Id=query_id)

        records = result["Records"]
        columns = result["ColumnMetadata"]
        colnames = [c["name"] for c in columns]
        rows = (self._parse_row(row) for row in records)
        df = pd.DataFrame(rows, columns=colnames)
        for col in columns:
            if "time" in col["typeName"]:
                df[col["name"]] = pd.to_datetime(df[col["name"]])

        return df

    def get_data(self, table, where="", sort="", limit=1000):
        limit = min(limit, 5000)
        where_clause = where and f"where {where}"
        sort_clause = sort and f"order by {sort}"
        return self.execute_query(
            f"select * from  {table} {where_clause} {sort_clause} limit {limit}"
        )
