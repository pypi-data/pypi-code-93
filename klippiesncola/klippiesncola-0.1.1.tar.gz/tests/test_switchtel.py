import unittest
from datetime import date
from klippiesncola.switchtel import Account, CallRecording


class TestAccount(unittest.TestCase):
    def setUp(self):
        self.account = Account()

    def test_login(self):
        self.assertEqual(self.account.login().status_code, 200)


class TestCallRecording(unittest.TestCase):
    def setUp(self):
        self.call_recording = CallRecording()

    def test_list(self):
        today = date.today().strftime("%Y-%m-%d")
        self.assertCountEqual(self.call_recording.list(today), list())


if __name__ == '__main__':
    unittest.main()
