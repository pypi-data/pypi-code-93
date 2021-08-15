from abc import ABC


class Player(ABC):
    def __init__(self, player_id: int, name: str):
        self._player_id = player_id
        self._name = name

    @property
    def player_id(self):
        return self._player_id

    @property
    def name(self):
        return self._name
