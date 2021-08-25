import unittest as unit
from humans_class import Humans
from orcs_class import Orcs
from party_class import Party
from board import Board

board = Board()
humans = Humans()
orcs = Orcs()
party = Party()


class Move:

    def __init__(self, start=(0, 0), finish=(0, 0), board=board.get_filledboard(), game=party):
        self.startrow = start[1]
        self.startcol = start[0]
        self.finishrow = finish[1]
        self.finishcol = finish[0]
        self.__moovingpiece = board[self.startrow][self.startcol]
        self.movelog = []
        self.moveID = self.startrow * 1000 + self.startcol * 100 + self.finishrow * 10 + self.finishcol
        self.__test = game

        self.__moveFunctions = {"kn": self.getknightmoves, "ma": self.getmagesmoves, "ca": self.getcatapultsmoves,
                                "or": self.getorcsmoves, "ar": self.getarchersmoves, "dr": self.getdrakesmoves}

        self.__knightsAndOrcsDirections = ((-1, 0), (0, -1), (1, 0), (0, 1), (-2, 0), (0, -2), (2, 0), (0, 2))
        self.__archersAndMagesDirections = ((-1, 1), (-1, -1), (1, -1), (1, 1), (-2, 2), (-2, -2), (2, -2), (2, 2))
        self.__catapultsAndDrakesDirections = ((-1, 1), (-1, -1), (1, -1), (1, 1), (-1, 0), (0, -1), (1, 0), (0, 1))

    def __eq__(self, other):
        """ overload of the = operation between 2 moves

        PRE : the other parameter must be an instance of the class Move
        POST : returns True if the 2 moves are the same or False if they aren't
        """
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getmovingpiece(self):
        return self.__moovingpiece

    def getallpossiblemoves(self, status):
        """

        return an array that contains all the possible moves

        PRE : status must be an array of array
        POST : return an array that contains instances of the class Move
        """
        moves = []
        for r in range(len(status)):
            for c in range(len(status[r])):
                if (status[r][c] in humans.get_nota()) or (
                        status[r][c] in orcs.get_notaOrcs()):
                    piece = status[r][c]
                    self.__moveFunctions[piece](r, c, moves, status)
        return moves

    def getknightmoves(self, row, col, moves, status):
        """

        generates Move instances of all knights pieces moves and put them into the moves array

        PRE : row, col must be integers and bigger then 0 and smaller then 12
              moves must be an empty array and status must be an array that contains 12 arrays of length 12.
        POST :inserts Move instences in the moves array
        """

        if self.__test.getTurn():
            for d in self.__knightsAndOrcsDirections:
                endrow = row + d[0]
                endcol = col + d[1]
                if 0 <= endrow < 12 and 0 <= endcol < 12:
                    endpiece = status[endrow][endcol]
                    if endpiece == "--":
                        moves.append(Move((col, row), (endcol, endrow), status))
                    else:
                        continue
                else:
                    continue

    def getarchersmoves(self, row, col, moves, status):
        """
        generates Move instances of all archers pieces moves and put them into the moves array

        PRE : row, col must be integers and bigger then 0 and smaller then 12
              moves must be an empty array and status must be an array that contains 12 arrays of length 12.
        POST :inserts all the possible archers Move instences in the moves array
        """

        if self.__test.getTurn():
            for d in self.__archersAndMagesDirections:
                endrow = row + d[0]
                endcol = col + d[1]
                if 0 <= endrow < 12 and 0 <= endcol < 12:
                    endpiece = status[endrow][endcol]
                    if endpiece == "--":
                        moves.append(Move((col, row), (endcol, endrow), status))
                    else:
                        continue
                else:
                    continue

    def getcatapultsmoves(self, row, col, moves, status):
        """

        generates Move instances of all catapults pieces moves and put them into the moves array

        PRE : row, col must be integers and bigger then 0 and smaller then 12
              moves must be an empty array and status must be an array that contains 12 arrays of length 12.
        POST :inserts all the possible catapults Move instences in the moves array
        """

        if self.__test.getTurn():
            for d in self.__catapultsAndDrakesDirections:
                endrow = row + d[0]
                endcol = col + d[1]
                if 0 <= endrow < 12 and 0 <= endcol < 12:
                    endpiece = status[endrow][endcol]
                    if endpiece == "--":
                        moves.append(Move((col, row), (endcol, endrow), status))
                    else:
                        continue
                else:
                    continue

    def getorcsmoves(self, row, col, moves, status):
        """
        generates Move instances of all orcs pieces moves and put them into the moves array

        PRE : row, col must be integers and bigger then 0 and smaller then 12
              moves must be an empty array and status must be an array that contains 12 arrays of length 12.
        POST :inserts all the possible orcs Move instences in the moves array
        """

        if not self.__test.getTurn():
            for d in self.__knightsAndOrcsDirections:
                endrow = row + d[0]
                endcol = col + d[1]
                if 0 <= endrow < 12 and 0 <= endcol < 12:
                    endpiece = status[endrow][endcol]
                    if endpiece == "--":
                        moves.append(Move((col, row), (endcol, endrow), status))
                    else:
                        continue
                else:
                    continue

    def getmagesmoves(self, row, col, moves, status):
        """
        generates Move instances of all mages pieces moves and put them into the moves array

        PRE : row, col must be integers and bigger then 0 and smaller then 12
              moves must be an empty array and status must be an array that contains 12 arrays of length 12.
        POST :inserts all the possible mages Move instences in the moves array
        """

        if not self.__test.getTurn():
            for d in self.__archersAndMagesDirections:
                endrow = row + d[0]
                endcol = col + d[1]
                if 0 <= endrow < 12 and 0 <= endcol < 12:
                    endpiece = status[endrow][endcol]
                    if endpiece == "--":
                        moves.append(Move((col, row), (endcol, endrow), status))
                    else:
                        continue
                else:
                    continue

    def getdrakesmoves(self, row, col, moves, status):
        """
        generates Move instances of all drakes pieces moves and put them into the moves array

        PRE : row, col must be integers and bigger then 0 and smaller then 12
              moves must be an empty array and status must be an array that contains 12 arrays of length 12.
        POST :inserts all the possible drakes Move instences in the moves array
        """

        if not self.__test.getTurn():
            for d in self.__catapultsAndDrakesDirections:
                endrow = row + d[0]
                endcol = col + d[1]
                if 0 <= endrow < 12 and 0 <= endcol < 12:
                    endpiece = status[endrow][endcol]
                    if endpiece == "--":
                        moves.append(Move((col, row), (endcol, endrow), status))
                    else:
                        continue
                else:
                    continue

    def makemove(self, move, status):
        """
        replace the initial position of a piece by '--' and replace the value of the destination by the code
        of the moving piece

        PRE : move must be an instance of the Move class and status must be an array that contains 12 arrays
                of length 12.
        POST :empty the starting position of the moving piece and fill the destination with his piece code
        """

        status[move.startrow][move.startcol] = '--'
        status[move.finishrow][move.finishcol] = move.getmovingpiece()
        move.movelog.append(move)
        self.__test.changingTurn()

class TestMoves(unit.TestCase):
    def test_getallpossiblemoves(self):
        test = Move()
        self.assertEqual(type(test.getallpossiblemoves(board.get_filledboard())), type([]))
        self.assertEqual(type(test.makemove(Move((2, 2), (4, 5)), board.get_filledboard())), type(None))
        self.assertEqual(type(test.getallpossiblemoves(board.get_filledboard())), type([]))

    def test_makemove(self):
        self.assertEqual(type(Move().makemove(Move((0, 0), (0, 0)), board.get_filledboard())), type(None))
