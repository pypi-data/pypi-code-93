import unittest
from pymongo.database import Database
from AsteriskRealtimeData.infrastructure.repositories.mongo.mongo_connection import (
    MongoConnection,
)


class TestMongoConnection(unittest.TestCase):
    def test_connection(self):
        mongo_connector = MongoConnection()
        connection = mongo_connector.get_connection()
        self.assertIsInstance(connection, Database)
