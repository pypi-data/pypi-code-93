import unittest
from weighting_platform.functions import general_functions
from qdk.main import QDK
from time import sleep


class GfTest(unittest.TestCase):
    def test_get_percent(self):
        first = 1000
        second = 500
        result_must = 50
        result = general_functions.get_change_percent(first, second)
        self.assertEqual(result, result_must)

    def test_send_status(self):
        qdk = QDK('localhost', 4455)
        qdk.make_connection()
        qdk.subscribe()
        while True:
            general_functions.send_status('SASD')
            print("RESPONSE:", qdk.get_data())
            sleep(1)

if __name__ == '__main__':
    unittest.main()
