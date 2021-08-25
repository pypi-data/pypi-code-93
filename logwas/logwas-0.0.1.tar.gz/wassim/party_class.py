from humans_class import Humans
from orcs_class import Orcs

h = Humans()
o = Orcs()


class Party:
    def __init__(self):
        self.__whiteturn = True
        self.__knightswins = True
        self.__orcswins = True
        self.__winner = None

    def getTurn(self):
        return self.__whiteturn

    def changingTurn(self):
        self.__whiteturn = not self.__whiteturn

    def knightswin(self, status):
        for i in range(0, 12):
            for u in range(0, 12):
                if status[i][u] in o.get_notaOrcs():
                    self.__knightswins = False
                else:
                    if self.__knightswins == False:
                        self.__knightswins = False
                    else:
                        self.__knightswins = True

    def orcswin(self, status):
        for i in range(0, 12):
            for u in range(0, 12):
                if status[i][u] in h.get_nota():
                    self.__orcswins = False
                else:
                    if self.__orcswins == False:
                        self.__orcswins = False
                    else:
                        self.__orcswins = True

    def getwinner(self):
        if self.__orcswins:
            return "or"
        elif self.__knightswins:
            return "kn"

    def getknightwinner(self):
        return self.__knightswins

    def getorcwinner(self):
        return self.__orcswins
