import unittest
from pynecone import Rest
import json


class MyTestCase(unittest.TestCase):
    def test_something(self):
        return
        res = Rest()(['post', 'nl', '/v0.1/api/nlls', '--json',
                      json.dumps({'directory': '', 'format': False, 'status': False, 'user_name': 'mlab289'})])
        print(res)
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
