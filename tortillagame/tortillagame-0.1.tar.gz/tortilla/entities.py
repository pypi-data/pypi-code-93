from abc import ABC, abstractmethod


class Entity(ABC):
    def __init__(self, owner, hp):
        self._killed = False
        self._owner = owner
        self._health_points = hp

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value):
        self._owner = value

    @property
    def health_points(self):
        return self._health_points

    @health_points.setter
    def health_points(self, value):
        self._health_points = value

    @property
    def is_killed(self):
        return self._killed

    @is_killed.setter
    def is_killed(self, value):
        self._killed = value


class Movable(Entity):
    def __init__(self, owner, hp, mp):
        super().__init__(owner, hp)
        self._move_points = mp

    @property
    def move_points(self):
        return self._move_points

    @move_points.setter
    def move_points(self, value):
        self._move_points = value


class Ship(Movable):
    def __init__(self, owner):
        super().__init__(owner, hp=3, mp=5)
        self._weapon_damage = 1

    @property
    def weapon_damage(self):
        return self._weapon_damage

    def set_default(self):
        self._move_points = 5


class Unmovable(Entity):
    def __init__(self, owner, hp):
        super().__init__(owner, hp)


class Obstacle(Unmovable):
    def __init__(self, owner):
        super().__init__(owner, hp=1)
