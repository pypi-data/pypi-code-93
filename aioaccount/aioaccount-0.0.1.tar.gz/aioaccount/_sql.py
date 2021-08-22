from typing import AsyncGenerator, Mapping, Optional
from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Binary,
    String,
    Boolean,
    func,
    select,
    and_ as sql_and,
    or_ as sql_or,
    create_engine,
    TIMESTAMP
)

from databases import Database

from ._const import _MAX_NAME_LEN


metadata = MetaData()

user_table = Table(
    "user",
    metadata,
    Column(
        "user_id",
        String(length=32),
        primary_key=True
    ),
    Column(
        "name",
        String(length=_MAX_NAME_LEN),
        nullable=True
    ),
    Column(
        "email",
        String(length=255),
        nullable=True
    ),
    Column(
        "email_vaildate",
        String(length=43),  # secrets.token_urlsafe(32)
        nullable=True
    ),
    Column(
        "password_reset_code",
        String(length=43),  # secrets.token_urlsafe(32)
        nullable=True
    ),
    Column(
        "password_reset_generated",
        TIMESTAMP,
        nullable=True
    ),
    Column(
        "email_confirmed",
        Boolean(),
        nullable=True
    ),
    Column(
        "password",
        Binary()
    ),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4"
)


def create_tables(url: str) -> None:
    if "mysql" in url:
        old_engine = "mysql"
        engine = "pymysql"
    elif "sqlite" in url:
        old_engine = "sqlite"
        engine = "sqlite3"
    elif "postgresql" in url:
        old_engine = "postgresql"
        engine = "psycopg2"
    else:
        assert False, "Invalid database URL engine."

    metadata.create_all(
        create_engine(url.replace(old_engine, f"{old_engine}+{engine}"))
    )


class SqlWrapper:
    """Doesn't cover SQL syntax entirely, but just
       includes needed functions.
    """

    def __init__(self, db: Database) -> None:
        self._db = db

        self._tables = {
            "user": user_table
        }

    def __convert_to_clauses(self, table: Table, dict_: dict) -> list:
        return [
            table.c[key] == value for key, value in dict_.items()
        ]

    async def exists(self, table: str,
                     or_: dict) -> bool:
        return await self._db.fetch_val(
            select([func.count()]).select_from(
                self._tables[table]
            ).where(
                sql_or(*self.__convert_to_clauses(self._tables[table], or_))
            )
        ) != 0

    async def delete(self, table: str,
                     and_: dict) -> None:
        await self._db.execute(
            self._tables[table].delete().where(
                sql_and(*self.__convert_to_clauses(self._tables[table], and_))
            )
        )

    async def update(self, table: str,
                     and_: dict, values: dict) -> None:
        await self._db.execute(
            self._tables[table].update().values(
                **values
            ).where(
                sql_and(*self.__convert_to_clauses(self._tables[table], and_))
            )
        )

    async def insert(self, table: str,
                     values: dict) -> None:
        await self._db.execute(
            self._tables[table].insert().values(
                **values
            )
        )

    async def get(self, table, and_: dict) -> Optional[Mapping]:
        return await self._db.fetch_one(
            self._tables[table].select().where(
                sql_and(*self.__convert_to_clauses(self._tables[table], and_))
            )
        )

    async def iterate(self, table: str, and_: dict = None
                      ) -> AsyncGenerator[Mapping, None]:
        query = self._tables[table].select()

        if and_:
            query = query.where(
                sql_and(*self.__convert_to_clauses(self._tables[table], and_))
            )

        async for row in self._db.iterate(query):
            yield row
