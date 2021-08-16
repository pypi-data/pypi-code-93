import unittest
from wengine.main import WEngine


class MainTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(MainTest, self).__init__(*args, **kwargs)
        self.wengine_test = WEngine('wdb', 'watchman', 'hect0r1337',
                                    '192.168.100.118')


if __name__ == '__main__':
    unittest.main()
