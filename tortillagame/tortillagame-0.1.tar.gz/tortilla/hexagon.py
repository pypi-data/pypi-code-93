class Hexagon:
    def __init__(self, x, y):
        self._entity = None
        self._x = x
        self._y = y
        self._neighbors = []
        # self.__directed = False
        # self.__selected = False

    @property
    def entity(self):
        return self._entity

    @entity.setter
    def entity(self, value):
        self._entity = value

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def coordinates(self):
        return self._x, self._y

    @property
    def neighbors(self):
        return self._neighbors

    @neighbors.setter
    def neighbors(self, value):
        self._neighbors = value
