""" Тесты клиента, получающего статус заезда """

import unittest
from qdk.main import QDK


class MainTest:
    def __init__(self, *args, **kwargs):
        super(MainTest, self).__init__(*args, **kwargs)
        self.status_qdk = QDK('localhost', 4455)
        self.status_qdk.make_connection()
        self.status_qdk.subscribe()

    def listen(self):
        while True:
            print('Answer:', self.status_qdk.get_data())


a = MainTest()
a.listen()