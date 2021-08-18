from qsct import functions
import unittest


class FunctionsTest(unittest.TestCase):
    def test_get_password_hash(self):
        response = functions.get_password_hash('123')
        response2 = functions.get_password_hash('123')
        self.assertTrue(response == response2)


if __name__ == '__main__':
    unittest.main()