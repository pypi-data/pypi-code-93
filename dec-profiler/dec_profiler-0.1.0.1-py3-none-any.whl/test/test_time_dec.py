import random
import unittest

from time_dec import *


class MyTestCase(unittest.TestCase):

    def test_time_s(self):
        @time_s(3)
        def test():
            a = []
            for i in range(7000):
                a.append(random.randint(0, 9))

        n = 100
        a = []
        test()

    def test_time_ns(self):
        @time_ns(3)
        def test():
            a = []
            for i in range(7000):
                a.append(random.randint(0, 9))

        n = 100
        a = []
        test()


if __name__ == '__main__':
    unittest.main()
