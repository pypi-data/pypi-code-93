# Created by Jan Rummens at 21/09/2020
import unittest
import time

from nemonet.screencast.recording import ScreenRecorder


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.screenRecorder  = ScreenRecorder()
        self.screenRecorder.start()

    def tearDown(self):
        self.screenRecorder.stop()

    def test_something(self):
        time.sleep(2)


if __name__ == '__main__':
    unittest.main()
