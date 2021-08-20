from ttgtcanvas2 import WorldModel, Maze
import random

def init(world):  
    choice = random.randint(1,10)
    world.add_object(1, 1, "daisy", 5)
    world.add_drop_obj_goal(5,1, "daisy", 1)
    

def generate_maze():
    world =  WorldModel('./worlds/test.json', init)
    return Maze(world)