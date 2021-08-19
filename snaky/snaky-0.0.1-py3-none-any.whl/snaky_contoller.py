from random import choice, sample, randint
from .snake import Snake
from .enums import CELL_STATE, DIRECTIONS, CELL_STATE_STR

class SnakyController():
    def __init__(self, w, h, on_kill=None, on_win=None) -> None:
        self.dimensions = w, h
        self.snakes = []
        self.world = [[CELL_STATE.EMPTY for _ in range(w)] for _ in range(h)]
        self.on_kill = on_kill
        self.on_win = on_win

    def step(self):
        for snake in sample(self.snakes, len(self.snakes)):
            head, tail = snake.step()

            if tail is not None:
                self.world[tail[1]][tail[0]] = CELL_STATE.EMPTY

            state = self.validate(head)

            if state == CELL_STATE.FOOD:
                snake.eat()
                self.world[head[1]][head[0]] = CELL_STATE.SNAKE
                f = self.make_food()
                if f is None:
                    self.finish(snake)
            elif state == CELL_STATE.EMPTY:
                self.world[head[1]][head[0]] = CELL_STATE.SNAKE
            elif state == CELL_STATE.OUTSIDE or state == CELL_STATE.SNAKE:
                self.kill(snake)
        
        return state

        
    def validate(self, pos):
        if pos is None:
            return CELL_STATE.OUTSIDE

        x, y = pos
        if x < 0 or x >= self.dimensions[0] or y < 0 or y >= self.dimensions[1]:
            return CELL_STATE.OUTSIDE

        return self.world[y][x]
    
    def hatch_snake(self, hatch_size=3):
        head = self.random_empty_pos()

        if head != None:
            s = Snake(head, choice(DIRECTIONS), hatch_size)
            self.set_to(head, CELL_STATE.SNAKE)
            self.snakes.append(s)

            return s
        return None

    def make_food(self):
        food = self.random_empty_pos()
        self.set_to(food, CELL_STATE.FOOD)
        return food
    
    def set_to(self, pos, state):
        self.world[pos[1]][pos[0]] = state
    
    def random_empty_pos(self):
        pos = None
        tries = 0
        max_tries = self.dimensions[0] * self.dimensions[1]

        while pos is None or self.validate(pos) != CELL_STATE.EMPTY and tries < max_tries:
            pos = randint(0, self.dimensions[0] - 1), randint(0, self.dimensions[1] - 1)
            tries += 1

        return pos
    
    def change_dir(self, snake, dir):
        self.snakes[snake].change_dir(dir)


    def kill(self, snake):
        if self.on_kill is not None:
            self.on_kill(snake, self)

    def finish(self, snake):
        if self.on_win is not None:
            self.on_win(snake, self)
    
    def __str__(self) -> str:
        return "\n".join([ ",".join([ CELL_STATE_STR[x] for x in y ]) for y in self.world])
