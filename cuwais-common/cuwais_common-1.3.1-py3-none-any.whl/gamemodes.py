import abc
import random
from typing import List

import chess as chess

from cuwais.config import config_file


class Gamemode:
    def __init__(self, name: str, players: List[str], options: dict):
        self._name = str(name)
        self._players = list(players)
        self._options = {"turn_time": 10, **dict(options)}

    @property
    def player_count(self):
        return len(self._players)

    @property
    def name(self):
        return self._name

    @property
    def players(self):
        return self._players.copy()

    @property
    def options(self):
        return self._options.copy()

    @abc.abstractmethod
    def setup(self, **options):
        """Gets the board that will be used by a game instance"""
        pass

    def filter_board(self, board, player: int):
        """Used to hide parts of the board, or transform the board into a form used by the player given"""
        return board

    def parse_move(self, move):
        """Optionally used to parse the returned move, eg if the AI can return a string or an object"""
        return move

    @abc.abstractmethod
    def is_move_legal(self, board, move) -> bool:
        """Checks if a move can be made with a given board"""
        pass

    @abc.abstractmethod
    def apply_move(self, board, move):
        """Applies the move to the board and returns the new board"""
        pass

    @abc.abstractmethod
    def is_win(self, board, player):
        """Checks if the board is in a won position given the player just moved"""
        pass

    @abc.abstractmethod
    def is_loss(self, board, player):
        """Checks if the board is in a lost position given the player just moved"""
        pass

    @abc.abstractmethod
    def is_draw(self, board, player):
        """Checks if the board is in a drawn position given the player just moved"""
        pass

    @abc.abstractmethod
    def encode_move(self, move, player) -> str:
        """Converts a move to a string form for storing or transmitting"""
        pass

    @abc.abstractmethod
    def encode_board(self, board) -> str:
        """Converts a board to a string form for storing or transmitting"""
        pass

    @staticmethod
    def get(gamemode_name):
        return {"chess": ChessGamemode()}.get(gamemode_name, None)

    @staticmethod
    def get_from_config():
        gamemode = Gamemode.get(config_file.get("gamemode.id").lower())
        options = config_file.get("gamemode.options")
        return gamemode, options


class ChessGamemode(Gamemode):
    def __init__(self):
        super(ChessGamemode, self).__init__(name="chess", players=["white", "black"], options={"chess_960": True})

    def setup(self, chess_960, **kwargs):
        if chess_960:
            return chess.Board.from_chess960_pos(random.randint(0, 959))

        return chess.Board()

    def is_win(self, board, move):
        return board.is_checkmate()

    def is_draw(self, board, move):
        return board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves()

    def is_loss(self, board, move):
        return False

    def parse_move(self, move):
        if isinstance(move, str):
            move = chess.Move.from_uci(move)
        return move

    def is_move_legal(self, board, move):
        if move is None:
            return False
        if not isinstance(move, chess.Move):
            return False
        if move not in board.legal_moves:
            return False
        return True

    def apply_move(self, board: chess.Board, move: chess.Move):
        board.push(move)
        return board

    def encode_move(self, move: chess.Move, player: int) -> str:
        return move.uci()

    def encode_board(self, board: chess.Board) -> str:
        return board.fen()
