import logging
import typing
import pandas as pd
import awswrangler as wr
from . import base


class DataStore(base.AWSClient):
    _bucket: str
    _database: str
    boto3_session = None

    def __init__(self, *, database: str=None, bucket: str=None, role_arn: str=None) -> None:
        super().__init__()
        if role_arn:
            self.boto3_session = self.session(role_arn=role_arn, role_session_name='Reporter', set_as_detault=True)
            logging.warning(f"Save boto3_session for awswrangler ({self.boto3_session})")
        self.bucket = bucket
        self.database = database

    @property
    def bucket(self) -> str:
        return f"s3://{self._bucket}" if self._bucket else ''

    @bucket.setter
    def bucket(self, name: str):
        self._bucket = name

    @property
    def database(self) -> str:
        return self._database

    @database.setter
    def database(self, name: str):
        self._database = name
        if name and name not in self.databases():
            self.create_database(name=name)
            logging.warning(f"Created database: {name}")

    def databases(self) -> list:
        dbs = wr.catalog.databases(boto3_session=self.boto3_session)
        return list(dbs.Database)

    def create_database(self, name: str):
        return wr.catalog.create_database(name, boto3_session=self.boto3_session)

    def tables(self):
        return wr.catalog.tables(database=self.database, boto3_session=self.boto3_session)

    def to_parquet(
            self,
            data: typing.Union[dict, list, pd.DataFrame],
            path: str=None,
            dataset=True,
            database: str=None,
            table: str=None,
            partition_cols=[],
            mode='overwrite_partitions',
            **kwargs) -> dict:
        """Save data as parquet, obviously doh!
        """
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data)
        if not database:
            # Set to object default
            database = self.database

        # Compile path to save data
        path = '/'.join(list(filter(None, [self.bucket, path, database, table])))

        if not path.startswith('s3://'):
            return data.to_parquet(path=path) #, engine='pyarrow'

        # Check that we have both database & table
        if not database or not table:
            dataset=False
            logging.warning(f"'database' or 'table' attribute(s) missing while saving to s3+glue ({path})? Force dataset=False")

        return wr.s3.to_parquet(
            df=data,
            path=path,
            dataset=dataset,
            database=database,
            table=table,
            partition_cols=partition_cols,
            mode=mode,
            **kwargs
        )

    def read_parquet(self, path: str, **kwargs) -> pd.DataFrame:
        if not path.startswith('s3://'):
            pd.read_parquet(path=path, engine='pyarrow')
        return wr.s3.read_parquet(
            path=path,
            dataset=True,
            **kwargs
        )

    def read_athena(self, query: str, **kwargs) -> pd.DataFrame:
        return wr.athena.read_sql_query(
            query,
            database=self.database,
            boto3_session=self.boto3_session,
            **kwargs
        )

    @staticmethod
    def fix_types(data) -> pd.DataFrame:
        df = pd.DataFrame(data)
        cctypes = {
            'unblended_cost': 'float',
            'blended_cost': 'float',
            'UnblendedCost': 'float',
            'BlendedCost': 'float',
            'period': 'int',
            'Period': 'int',
            'linked_account': 'string',
            'LinkedAccount': 'string',
            # 'Start': 'date'
            # 'End': 'date'
        }
        for cname, ctype in cctypes.items():
            if cname not in df.columns:
                continue
            if ctype == 'date':
                data[cname] = pd.to_datetime(data[cname])
                data[cname] = data[cname].dt.date
            else:
                df[cname] = df[cname].astype(ctype)
        return df
