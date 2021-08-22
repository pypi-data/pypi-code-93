from typing import AsyncGenerator, Mapping, Optional
from motor.motor_asyncio import AsyncIOMotorClient


class MongoWrapper:
    """Doesn't cover mongo syntax entirely, but just
       includes needed functions.
    """

    def __init__(self, db: AsyncIOMotorClient) -> None:
        self._db = db

    async def exists(self, table: str, or_: dict) -> bool:
        return await self._db[table].count_documents(
            {"$or": [{key: value} for key, value in or_.items()]}
        ) != 0

    async def delete(self, table: str,
                     and_: dict) -> None:
        await self._db[table].delete_many(and_)

    async def update(self, table: str,
                     and_: dict, values: dict) -> None:
        await self._db[table].update_one(
            and_,
            {"$set": values}
        )

    async def insert(self, table: str,
                     values: dict) -> None:
        await self._db[table].insert_one(values)

    async def get(self, table, and_: dict) -> Optional[Mapping]:
        return await self._db[table].find_one(and_)

    async def iterate(self, table: str, and_: dict = None
                      ) -> AsyncGenerator[Mapping, None]:
        find = self._db[table].find(and_) if and_ else self._db[table].find()

        async for document in find:
            yield document
