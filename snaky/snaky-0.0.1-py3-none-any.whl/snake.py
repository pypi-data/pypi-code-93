from queue import Queue
from .enums import Direction

class Snake():

    def __init__(self, head, direction, pre_food) -> None:
        self.tail = Queue()
        self.direction = direction
        self.last_step = direction
        self.food = pre_food
        self.pre_food = pre_food
        self.head = head
        self.tail.put(head)

    def step(self):
        if self.direction == Direction.UP:
            self.head = self.head[0], self.head[1] - 1
        elif self.direction == Direction.DOWN:
            self.head = self.head[0], self.head[1] + 1
        elif self.direction == Direction.LEFT:
            self.head = self.head[0] - 1, self.head[1]
        elif self.direction == Direction.RIGHT:
            self.head = self.head[0] + 1, self.head[1]

        self.last_step = self.direction

        tail = None
        if self.food > 0:
            self.food -= 1
        else:
            tail = self.tail.get()

        self.tail.put(self.head)

        return self.head, tail
    
    def eat(self):
        self.food += 1

    def change_dir(self, new_dir):
        if self.last_step == Direction.UP and new_dir != Direction.DOWN:
            self.direction = new_dir
        elif self.last_step == Direction.DOWN and new_dir != Direction.UP:
            self.direction = new_dir
        elif self.last_step == Direction.LEFT and new_dir != Direction.RIGHT:
            self.direction = new_dir
        elif self.last_step == Direction.RIGHT and new_dir != Direction.LEFT:
            self.direction = new_dir
        
        return self.direction
    
    def size(self):
        return self.tail.qsize()
