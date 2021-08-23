from __future__ import annotations

import typing as t
from inspect import isclass

from aio_databases import Database
from pypika.queries import (
    Column,
    CreateQueryBuilder,
    Query,
    QueryBuilder,
    builder,
)


class ModelDBMixin:

    _db: t.Optional[Database]
    _model: Model

    get_sql: t.Callable[..., str]

    def execute(self, *args, **kwargs) -> t.Awaitable:
        assert self._db, 'DB is not inited'
        sql = self.get_sql()
        return self._db.execute(sql, *args, **kwargs)

    def executemany(self, *args, **kwargs) -> t.Awaitable:
        assert self._db, 'DB is not inited'
        sql = self.get_sql()
        return self._db.executemany(sql, *args, **kwargs)

    async def fetchall(self, *args, **kwargs) -> t.List[Model]:
        assert self._db, 'DB is not inited'
        sql = self.get_sql()
        records = await self._db.fetchall(sql, *args, **kwargs)
        return [self._model(**dict(rec.items())) for rec in records]

    async def fetchone(self, *args, **kwargs) -> t.Optional[Model]:
        assert self._db, 'DB is not inited'
        sql = self.get_sql()
        rec = await self._db.fetchone(sql, *args, **kwargs)
        if rec is None:
            return rec

        return self._model(**dict(rec.items()))

    def fetchval(self, *args, **kwargs) -> t.Awaitable:
        assert self._db, 'DB is not inited'
        sql = self.get_sql()
        return self._db.fetchval(sql, *args, **kwargs)


class ModelQueryBuilder(QueryBuilder, ModelDBMixin):

    def __init__(self, model: Model, *, db: Database = None, **kwargs):
        self._model = model
        self._db = db
        super(ModelQueryBuilder, self).__init__(**kwargs)
        self._from = [model]

    def __copy__(self) -> ModelQueryBuilder:
        newone = super(ModelQueryBuilder, self).__copy__()
        newone._model = self._model
        return newone

    def select(self, *terms: t.Any) -> ModelQueryBuilder:
        if not (terms or self._selects):
            terms = self._model,

        prepared_terms = []
        for term in terms:
            if isclass(term) and issubclass(term, Model):
                prepared_terms += [f for f in term.meta.fields.values()]
            else:
                prepared_terms.append(term)

        return super(ModelQueryBuilder, self).select(*prepared_terms)

    @builder
    def insert(self, *terms: t.Any, **kwargs):
        self._insert_table = self._model
        if terms:
            return super(ModelQueryBuilder, self).insert(*terms)

        model = self._model
        columns, values = zip(*kwargs.items())
        for name in columns:
            field = getattr(model, name, None)
            if field is None:
                continue

            self._columns.append(field)

        self._apply_terms(*values)
        self._replace = False

    @builder
    def update(self):
        if self._update_table is not None or self._selects or self._delete_from:
            raise AttributeError("'Query' object has no attribute '%s'" % "update")

        self._from = []
        self._update_table = self._model

    #  def join(self, item: t.Any, how: JoinType = JoinType.inner) -> ModelQueryBuilder:
    #      if issubclass(item, Model):
    #          item = item.meta.table

    #      return super(ModelQueryBuilder, self).join(item, how=how)

    def create_table(self) -> ModelCreateQueryBuilder:
        return ModelCreateQueryBuilder(db=self._db, dialect=self.dialect).create_table(self._model)


class ModelCreateQueryBuilder(CreateQueryBuilder, ModelDBMixin):

    def __init__(self, db: Database = None, **kwargs):
        super(ModelCreateQueryBuilder, self).__init__(**kwargs)
        self._db = db

    def create_table(self, item: t.Any) -> ModelCreateQueryBuilder:
        if isclass(item) and issubclass(item, Model):
            meta = item.meta
            builder = super(ModelCreateQueryBuilder, self).create_table(meta.table)
            columns = [Column(field.name, column_type=field.db_type,
                              default=field.default, nullable=field.null)
                       for field in meta.fields.values()]

            builder = builder.columns(*columns)
            if meta.primary_key:
                builder = builder.primary_key(*meta.primary_key)
            return builder

        return super(ModelCreateQueryBuilder, self).create_table(item)


from .model import Model  # noqa
