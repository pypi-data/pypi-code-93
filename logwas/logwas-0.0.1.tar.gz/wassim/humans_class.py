import unittest as unit


class Humans:
    def __init__(self, kng=4, arch=6, cata=2):
        self.__nbrknights = kng
        self.__nbrarch = arch
        self.__nbrcata = cata
        self.__nota = ["kn", "ar", "ca"]
        self.__carac = {

            "kn": {"porte": 2, "dep": 2, "points": 10},
            "ar": {"porte": 4, "dep": 4, "points": 30},
            "ca": {"porte": 6, "dep": 3, "points": 50}

        }

    @property
    def get_nbrknights(self):
        return self.__nbrknights

    @property
    def get_nbrarch(self):
        return self.__nbrarch

    @property
    def get_nbrcata(self):
        return self.__nbrcata

    @get_nbrknights.setter
    def get_nbrknights(self, value):
        self.__nbrknights = value

    @get_nbrarch.setter
    def get_nbrarch(self, value):
        self.__nbrarch = value

    @get_nbrcata.setter
    def get_nbrcata(self, value):
        self.__nbrcata = value

    def kill_chev(self):
        self.__nbrknights -= 1

    def kill_arch(self):
        self.__nbrarch -= 1

    def kill_cata(self):
        self.__nbrcata -= 1

    def get_nota(self):
        return self.__nota


class TestHuman(unit.TestCase):
    def test_getnotation(self):
        self.assertEqual(type(Humans().get_nota()), type([]))
        for i in range(0, 3):
            self.assertEqual(type(Humans().get_nota()[i]), type(""))
