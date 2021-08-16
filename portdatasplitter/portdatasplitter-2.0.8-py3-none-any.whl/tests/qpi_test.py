import unittest
from qdk.main import QDK
from time import sleep


class QdkTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(QdkTest, self).__init__(*args, **kwargs)
        self.qdk = QDK('192.168.100.118', 2292)
        self.qdk.make_connection()

    def test_set_null(self):
        res = self.qdk.execute_method('set_manual_value', manual_value=0,
                                get_response=True)
        print('res', res)
        weight = self.qdk.execute_method('get_value', get_response=True)
        print('weight', weight)
        sleep(2)
        weight = self.qdk.execute_method('get_value', get_response=True)
        print('weight', weight)


