import unittest


class Army:
    def __init__(self):
        self.__nombrepieces = 24
        self.__equipeorcs = 12
        self.__teamhuman = 12
        self.__nbrhumainmort = 0
        self.__nbrorcmort = 0

    @property
    def get_nbrhuman(self):
        return self.__teamhuman


class Testarmy(unittest.TestCase):
    def test_get_nbrhuman(self):
        self.assertEqual(type(Army().get_nbrhuman), type(4))
        self.assertEqual(Army().get_nbrhuman, 12)
