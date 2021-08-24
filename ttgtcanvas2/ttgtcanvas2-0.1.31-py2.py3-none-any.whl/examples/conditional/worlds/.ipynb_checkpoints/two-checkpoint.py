from ttgtcanvas2 import WorldModel, Maze
import random

def init(world):
    flip = random.randint(0,1)
    left=4; right=10; bottom=3; top=7
    
    tx1 = random.randint(left  + 1 ,right - 1)
    tx2 = random.randint(left + 1,right -1)
    ry1 = random.randint(bottom + 1,top - 1)
    
    world.remove_wall(tx1, top, "north")
    world.add_goal_wall(tx1, top, "north")
    
    world.remove_wall(tx2, bottom, "south")
    world.add_goal_wall(tx2, bottom, "south")
    
    world.remove_wall(right, ry1, "east")
    world.add_goal_wall(right, ry1, "east")
    

def generate_maze():
    world =  WorldModel('./worlds/two.json', init)
    return Maze(world)