from enum import Enum, auto

class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

DIRECTIONS = list(Direction)

class CELL_STATE(Enum):
    OUTSIDE = -1
    EMPTY = 0
    FOOD = 1
    WALL = 2
    SNAKE = 3

CELL_STATE_STR = {
    CELL_STATE.OUTSIDE: "-",
    CELL_STATE.EMPTY: "+",
    CELL_STATE.FOOD: "@",
    CELL_STATE.WALL: "#",
    CELL_STATE.SNAKE: "O",
}
