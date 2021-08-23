import typing as t

from aio_databases import Database
from pypika.enums import Dialects

from .model import Model
from .query import ModelQueryBuilder


_dialects = {'sqlite': 'sqllite'}


class Manager:
    """Manage database and models."""

    def __init__(self, database: t.Union[Database, str]):
        if isinstance(database, str):
            database = Database(database)

        self.db = database
        self.dialect = Dialects(_dialects.get(database.backend.name, database.backend.name))

    def __call__(self, model: Model, **kwargs) -> ModelQueryBuilder:
        return ModelQueryBuilder(model, db=self.db, dialect=self.dialect, **kwargs)

    async def __aenter__(self):
        await self.db.__aenter__()
        return self

    def __aexit__(self, *args):
        return self.db.__aexit__(*args)

    def __getattr__(self, name: str):
        return getattr(self.db, name)
