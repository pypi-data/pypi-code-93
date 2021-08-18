import unittest
from qdk import functions
from qdk.methods import methods_dict


class FunctionsTest(unittest.TestCase):
    def test_get_method(self):
        response = functions.get_method(methods_dict, 'hello_world')
        self.assertTrue(response['method'] == 'hello_world')


if __name__ == '__main__':
    unittest.main()
