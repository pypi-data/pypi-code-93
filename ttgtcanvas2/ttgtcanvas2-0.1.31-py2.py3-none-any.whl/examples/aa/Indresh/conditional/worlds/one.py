from ttgtcanvas2 import WorldModel, Maze
import random

def init(world):
    r = random.randint(3,10)
    c = random.randint(3,10)
    world.set_dimensions(r,c)
    
    for x in range(2,c):
        for y in range(2, r):
            world.add_tile(x, y, 'water')
    
    for x in range(1,c + 1):
        world.add_tile(x, 1, 'grass')
        world.add_tile(x, r, 'grass')

    for y in range(1,r + 1):
        world.add_tile(1, y, 'grass')
        world.add_tile(c, y, 'grass')
    
    for y in range(2,r):
        world.add_wall(1, y, "east")
        world.add_wall(c - 1, y, "east")

    for x in range(2,c):
        world.add_wall(x, 1, "north")
        world.add_wall(x, r -1, "north")
     
    world.add_wall(1, 1, "north")
    world.add_object(1,2,"carrot", 1)
        

    

def generate_maze():
    world =  WorldModel('./worlds/one.json', init)
    return Maze(world)