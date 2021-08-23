from __future__ import annotations

import typing as t

from pypika.dialects import (
    Dialects, PostgreSQLQueryBuilder,
    MySQLQuery, MySQLQueryBuilder, SQLLiteQueryBuilder
)

from .query import ModelBuilderMixin, ModelQuery, ModelCreateQueryBuilder, ModelDropQueryBuilder


DIALECT_TO_BUILDER = {}


# Postgres
# --------

class ModelPostgreSQLQuery(ModelQuery):

    @classmethod
    def _builder(cls, **kwargs) -> ModelMySQLQueryBuilder:
        return ModelPostgreSQLQueryBuilder(**kwargs)


class ModelPostgreSQLQueryBuilder(ModelBuilderMixin, PostgreSQLQueryBuilder):

    QUERY_CLS = ModelPostgreSQLQuery


DIALECT_TO_BUILDER[Dialects.POSTGRESQL] = ModelPostgreSQLQueryBuilder


# MySQL
# -----

class ModelMySQLCreateQueryBuilder(ModelCreateQueryBuilder):

    QUOTE_CHAR = MySQLQueryBuilder.QUOTE_CHAR


class ModelMySQLDropQueryBuilder(ModelDropQueryBuilder):

    QUOTE_CHAR = MySQLQueryBuilder.QUOTE_CHAR


class ModelMySQLQuery(MySQLQuery):

    @classmethod
    def _builder(cls, **kwargs) -> ModelMySQLQueryBuilder:
        return ModelMySQLQueryBuilder(**kwargs)

    @classmethod
    def create_table(cls, table: t.Union[str, t.Table], **kwargs) -> ModelCreateQueryBuilder:
        return ModelMySQLCreateQueryBuilder(**kwargs).create_table(table)

    @classmethod
    def drop_table(cls, table: t.Union[str, t.Table], **kwargs) -> ModelCreateQueryBuilder:
        return ModelMySQLDropQueryBuilder(**kwargs).drop_table(table)


class ModelMySQLQueryBuilder(ModelBuilderMixin, MySQLQueryBuilder):

    QUERY_CLS = ModelMySQLQuery


DIALECT_TO_BUILDER[Dialects.MYSQL] = ModelMySQLQueryBuilder


# SQLite
# ------

class ModelSQLLiteQuery(ModelQuery):

    @classmethod
    def _builder(cls, **kwargs) -> ModelMySQLQueryBuilder:
        return ModelSQLLiteQueryBuilder(**kwargs)


class ModelSQLLiteQueryBuilder(ModelBuilderMixin, SQLLiteQueryBuilder):

    QUERY_CLS = ModelSQLLiteQuery


DIALECT_TO_BUILDER[Dialects.SQLLITE] = ModelSQLLiteQueryBuilder
