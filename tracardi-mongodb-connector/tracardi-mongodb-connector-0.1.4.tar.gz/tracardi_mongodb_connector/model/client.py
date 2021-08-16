import pymongo
from motor.motor_asyncio import AsyncIOMotorClient

from tracardi_mongodb_connector.model.configuration import MongoConfiguration


class MongoClient1:
    def __init__(self, config: MongoConfiguration):
        self.config = config
        self.client = pymongo.MongoClient(config.uri, serverSelectionTimeoutMS=config.timeout)

    def find(self, database, collection, query):
        database = self.client[database]
        collection = database.get_collection(collection)
        return collection.find(query)


class MongoClient:
    def __init__(self, config: MongoConfiguration):
        self.config = config
        self.client = AsyncIOMotorClient(config.uri)

    async def find(self, database, collection, query):

        async def _fetch(cursor):
            async for document in cursor:
                yield document

        database = self.client[database]
        collection = database[collection]
        return [d async for d in collection.find(query)]
