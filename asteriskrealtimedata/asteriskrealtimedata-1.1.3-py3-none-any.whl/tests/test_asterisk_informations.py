import unittest

from AsteriskRealtimeData.infrastructure.repositories.mongo.mongo_connection import MongoConnection
from AsteriskRealtimeData.asterisk_informations import AsteriskInformations
from AsteriskRealtimeData.domain.pause_reason.pause_reason import PauseReason


class TestAsteriskInformations(unittest.TestCase):
    def test_create_pause_reason(self):
        mongo_database = MongoConnection()
        asterisk_informations = AsteriskInformations(mongo_database)

        result = asterisk_informations.insert_or_update_pause_reason(pause_reason=PauseReason("1001", "Testing2"))

        a = result.raw_result
        b = result.upserted_id
        c = result.modified_Count
        d = result.matched_count
        print("Resultado final:", result.raw_result)
        print("Resultado final id:", result.upserted_id)
        if "updatedExisting" in result:
            self.assertEqual(result.modifiedCount(), 1)
        else:
            self.assertEqual(result.matchedCount(), 1)
