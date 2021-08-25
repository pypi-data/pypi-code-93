from humans_class import Humans
from orcs_class import Orcs
from board import Board
import unittest as unit

board = Board()
human = Humans()
orcs = Orcs()


class Attack:
    def __init__(self, piece=(0, 0), attack=(0, 0), board=board.get_filledboard()):
        self.__attackerrow = piece[1]
        self.__attackercol = piece[0]
        self.__attackedrow = attack[1]
        self.__attackedcol = attack[0]
        self.__attackedpiece = board[self.__attackedrow][self.__attackedcol]
        self.__knightsTurn = True

        self.attackID = self.__attackerrow * 1000 + self.__attackercol * 100 + self.__attackedrow * 10 + self.__attackedcol

        self.attackFunctions = {"kn": self.getnightattacks, "ma": self.getmagesattacks,
                                "ca": self.getcatapultsattacks,
                                "or": self.getorcsattacks, "ar": self.getarchersattacks,
                                "dr": self.getdrakesattacks}
        self.__knightsAndOrcsAttacksRadius = ((-1, 1), (-1, -1), (1, -1), (1, 1), (-1, 0), (0, -1), (1, 0), (0, 1))
        self.__archersAndMagesAttacksRadius = ((-1, 0), (0, -1), (1, 0), (0, 1))

    def __eq__(self, other):
        """
        overload of the = operation between 2 attacks

        PRE : the other parameter must be an instance of the class Attack
        POST : returns True if the 2 attacks are the same or False if they aren't
        """

        if isinstance(other, Attack):
            return self.attackID == other.attackID
        return False

    def getallpossibleattacks(self, status):
        """

        return an array that contains all the possible attacks

        PRE : status must be an array that contains 12 arrays of length = 12
        POST : return an array that contains instances of the class Attack
        """
        attacks = []
        for r in range(len(status)):
            for c in range(len(status[r])):
                if (status[r][c] in human.get_nota()) or (
                        status[r][c] in orcs.get_notaOrcs()):
                    piece = status[r][c]
                    self.attackFunctions[piece](r, c, attacks, status)
        return attacks

    def makeattacks(self, attacks, status):
        """
        replace the target position by '--' and change the turn

        PRE : attacks must be an instance of the Attack class and status must be an array that contains 12 arrays
                of length 12.
        POST :replace the target by '--' and inverse the turn
        """
        status[attacks.__attackedrow][attacks.__attackedcol] = '--'
        print(attacks.__attackedpiece)
        self.__knightsTurn = not self.__knightsTurn

    def getnightattacks(self, row, col, attacks, status):
        """
        create Attack instances for all knights pieces possible attacks and put them into the moves array

        PRE : row, col must be integers and bigger then 0 and smaller then 12
              attacks must be an array and status must be an array that contains 12 arrays of length 12.
        POST :inserts Attack instences in the attacks array
        """

        if self.__knightsTurn:
            for d in self.__knightsAndOrcsAttacksRadius:
                endrow = row + d[0]
                endcol = col + d[1]
                attacks.append(Attack((col, row), (endcol, endrow), status))

    def getarchersattacks(self, row, col, attacks, status):
        """
        create Attack instances of all archers pieces attacks and put them into an array array

        PRE : row, col must be integers and bigger then 0 and smaller then 12
              attacks must be an array and status must be an array that contains 12 arrays of length 12.
        POST :inserts all the possible archers Attack instences in the attacks array
        """
        if self.__knightsTurn:
            for d in self.__archersAndMagesAttacksRadius:
                for i in range(2, 6):
                    endrow = row + d[0] * i
                    endcol = col + d[1] * i
                    if 0 <= endrow < 12 and 0 <= endcol < 12:
                        attacks.append(Attack((col, row), (endcol, endrow), status))
                    else:
                        break

    def getcatapultsattacks(self, row, col, attacks, status):
        """
        create Attack instances of all catapults pieces attacks and put them into the attacks array

        PRE : row, col must be integers and bigger then 0 and smaller then 12
              attacks must be an array and status must be an array that contains 12 arrays of length 12.
        POST :inserts all the possible catapults Attack instences in the attacks array
        """

        if self.__knightsTurn:

            for i in range(6, 8):
                endrow = row - i
                for u in range(1, 12):
                    endcol = u
                    if 0 <= endrow < 12 and 0 <= endcol < 12:
                        attacks.append(Attack((col, row), (endcol, endrow), status))
                    else:
                        break

    def getorcsattacks(self, row, col, attack, status):
        """
        create Attack instances for all orcs pieces attacks and put them into the moves array

        PRE : row, col must be integers and bigger then 0 and smaller then 12
              attacks must be an empty array and status must be an array that contains 12 arrays of length 12.
        POST :inserts all the possible orcs Attack instences in the attacks array
        """

        if not self.__knightsTurn:
            for d in self.__knightsAndOrcsAttacksRadius:
                endrow = row + d[0]
                endcol = col + d[1]
                attack.append(Attack((col, row), (endcol, endrow), status))

    def getmagesattacks(self, row, col, attacks, status):
        """
        create Attack instances for all mages pieces attacks and put them into the attacks array

        PRE : row, col must be integers and bigger then 0 and smaller then 12
              attacks must be an array and status must be an array that contains 12 arrays of length 12.
        POST :inserts all the possible mages Attack instences in the attacks array
        """

        if not self.__knightsTurn:
            for d in self.__archersAndMagesAttacksRadius:
                for i in range(2, 6):
                    endrow = row + d[0] * i
                    endcol = col + d[1] * i
                    if 0 <= endrow < 12 and 0 <= endcol < 12:
                        attacks.append(Attack((col, row), (endcol, endrow), status))
                    else:
                        break

    def getdrakesattacks(self, row, col, attacks, status):
        """
        create Attack instances of all drakes pieces attacks and put them into the attacks array

        PRE : row, col must be integers and bigger then 0 and smaller then 12
              attacks must be an empty array.
              status must be an array that contains 12 arrays of length 12.
        POST :inserts all the possible drakes Attack instences in the attacks array
        """

        if not self.__knightsTurn:
            for i in range(6, 8):
                endrow = row + i
                for u in range(1, 12):
                    endcol = u
                    if 0 <= endrow < 12 and 0 <= endcol < 12:
                        attacks.append(Attack((col, row), (endcol, endrow), status))
                    else:
                        break


class TestAttack(unit.TestCase):
    def test_getallpossibleattacks(self):
        test = Attack()
        self.assertEqual(type(test.getallpossibleattacks(board.get_filledboard())), type([]))
        self.assertEqual(type(test.makeattacks(Attack((0, 1), (0, 2)), board.get_filledboard())), type(None))
        self.assertEqual(type(test.getallpossibleattacks(board.get_filledboard())), type([]))

    def test_makeattack(self):
        self.assertEqual(type(Attack().makeattacks(Attack((0, 1), (0, 2)), board.get_filledboard())), type(None))
