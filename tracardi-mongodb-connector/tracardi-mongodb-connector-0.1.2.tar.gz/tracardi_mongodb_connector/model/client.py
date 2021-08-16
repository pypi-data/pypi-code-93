import pymongo
import motor

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
        self.client = motor.motor_asyncio.AsyncIOMotorClient(config.uri)

    def find(self, database, collection, query):
        database = self.client[database]
        collection = database[collection]
        return await collection.find(query)
