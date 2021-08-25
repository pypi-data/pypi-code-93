class Orcs:
    def __init__(self):
        self.__nbrorcs = 4
        self.__nbrmages = 6
        self.__nbrdrakes = 2
        self.__nota = ["or", "ma", "dr"]

        self.__carac = {

            "or": {"porte": 2, "dep": 2, "points": 10},
            "ma": {"porte": 4, "dep": 3, "points": 30},
            "dr": {"porte": 6, "dep": 4, "points": 50}

        }

    def get_nbrorcs(self):
        return self.__nbrorcs

    def get_nbr_mages(self):
        return self.__nbrmages

    def get_nbrdrakes(self):
        return self.__nbrdrakes

    def kill_orc(self):
        self.__nbrorcs -= 1

    def kill_mag(self):
        self.__nbrmages -= 1

    def kill_drake(self):
        self.__nbrdrakes -= 1

    def get_notaOrcs(self):
        return self.__nota
