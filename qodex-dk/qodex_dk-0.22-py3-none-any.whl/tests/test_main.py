from qdk.main import QDK
import unittest


class MainTets(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.qdk_test = QDK('localhost', 1337, 'testuser', 'testpass')

    def test_get_sdk_methods(self):
        response = self.qdk_test.get_sdk_methods()
        print(response)

    def test_no_socket_exc(self):
        response = self.qdk_test.execute_method('TEST', get_response=True)
        print(response)


if __name__ == '__main__':
    unittest.main()