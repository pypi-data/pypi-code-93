from typing import Union, List

from pandas import DataFrame, read_sql
from pymongo.errors import CollectionInvalid
from pymongo import DESCENDING, ASCENDING
from sqlalchemy import MetaData, Table, Column, select
from sqlalchemy.orm import Query
from sqlalchemy.sql import Select, Alias
from sqlalchemy.sql.selectable import CompoundSelect
from sqlalchemy.sql.elements import BooleanClauseList, BinaryExpression

from stakenix.core.connectors import (
    ClickHouseConnector,
    PostgreSQLConnector,
    MySQLConnector,
    MsSQLConnector,
    MongoDBSSHConnector,
    MongoDBDirectConnector
)
from stakenix.utils import bson_to_string, flatten


class Database:
    def __init__(self) -> None:
        self._cls_connector = None
        self._schema = None
        self._database = None

    def query(self) -> None:
        raise NotImplementedError


class SQLDatabase(Database):
    def __init__(self) -> None:
        self.session = self._cls_connector(self._schema, self._database)._generate_session()

    def get_table(self, table: str) -> Table:
        return self._get_reflected_table(table)

    def _get_reflected_table(self, table: str) -> Table:
        if not isinstance(table, str):
            raise ValueError("table must be str object")

        return Table(table, MetaData(), autoload_with=self.session.connection(), schema=self._schema)

    def build_subquery(self, query: Query) -> Alias:
        return self.build_query(query).subquery()

    def build_query(self, query: Query) -> Query:
        if not isinstance(query, Query):
            raise ValueError("query must be object of Query")

        return query.with_session(self.session)

    def from_query_obj(self, query: Union[Query, Select, CompoundSelect], **kwargs) -> DataFrame:
        if isinstance(query, Query):
            query_obj = query.statement
        elif isinstance(query, (Select, Alias, CompoundSelect)):
            query_obj = query
        else:
            raise ValueError("query must be instance of class Query or Select")

        return read_sql(query_obj, self.session.connection(), **kwargs)

    def query(
        self,
        table: str,
        columns: List[Column],
        where: Union[BinaryExpression, BooleanClauseList] = None,
        group_by: Union[Column, List[Column]] = None,
        having: Union[Column, List[Column]] = None,
        order_by: Union[Column, List[Column]] = None,
        limit: int = None,
        in_dict: bool = False,
        **kwargs,
    ) -> DataFrame:

        with self._cls_connector(self._schema, self._database).connection() as sess:
            query = select(
                from_obj=self._get_reflected_table(table),
                columns=columns,
                whereclause=where,
                group_by=group_by,
                having=having,
                order_by=order_by,
                **kwargs,
            ).limit(limit)
            if in_dict:
                cursor = sess.execute(query)
                return [dict(row) for row in cursor]
            else:
                return read_sql(sql=query, con=sess.connection())

    def __del__(self):
        try:
            self.session.close()
        except AttributeError:
            pass


class NoSQLDatabase(Database):
    def __init__(self) -> None:
        super().__init__()

    def query(
        self,
        table: str,
        columns: List[str] = None,
        where: dict = None,
        order_by: Union[List[str], str] = None,
        desc: Union[List[bool], bool] = False,
        limit: int = 0,
        in_dict: bool = False
    ) -> DataFrame:

        with self._cls_connector(self._schema).connection() as conn:
            if not table in conn.list_collection_names():
                raise CollectionInvalid(
                    f"Collection: {table} doesn't exists in database {conn.name}"
                )
            if order_by is None:
                query = conn[table].find(filter=where, limit=limit, projection=columns)
            else:
                query = (
                    conn[table]
                    .find(filter=where, limit=limit, projection=columns)
                    .sort(
                        [(order_by, DESCENDING if desc else ASCENDING)]
                        if isinstance(order_by, str)
                        else list(zip(order_by, [DESCENDING if level else ASCENDING for level in desc]))
                    )
                )
            if in_dict:
                return [row for row in query]
            else:
                result = DataFrame(iter(query)).pipe(bson_to_string).pipe(flatten)
                return result


class PostgreDB(SQLDatabase):
    def __init__(self, schema: str = "customdata", database: str = "default") -> None:
        self._cls_connector = PostgreSQLConnector
        self._schema = schema
        self._database = database
        super().__init__()


class MySQL(SQLDatabase):
    def __init__(self, schema: str, database: str = "default") -> None:
        self._cls_connector = MySQLConnector
        self._schema = schema
        self._database = database
        super().__init__()


class MsSQL(SQLDatabase):
    def __init__(self, schema: str = "dbo", database: str = "default") -> None:
        self._cls_connector = MsSQLConnector
        self._schema = schema
        self._database = database
        super().__init__()


class ClickHouse(SQLDatabase):
    def __init__(self, schema: str, database: str = "default") -> None:
        self._cls_connector = ClickHouseConnector
        self._schema = schema
        self._database = database
        super().__init__()


class MongoDB(NoSQLDatabase):
    def __init__(self, schema: str, via_ssh: bool = True) -> None:
        super().__init__()
        if via_ssh:
            self._cls_connector = MongoDBSSHConnector
        else:
            self._cls_connector = MongoDBDirectConnector
        
        self._schema = schema