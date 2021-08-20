from ttgtcanvas2 import WorldModel, Maze
import random

def init(world):
    nb_carrot = 0
    nb_apple = 0
    h = 12
    w = 12
    for x in range(2, w + 1):
        choice = random.randint(1,3)
        if choice == 1:
            world.add_object(x, 1, "carrot", 1)
            nb_carrot += 1
        elif choice == 2:
            world.add_object(x, 1,"apple", 1)
            nb_apple += 1
    
    for y in range(2, h + 1):
        choice = random.randint(1,3)
        if choice == 1:
            world.add_object(w, y, "carrot", 1)
            nb_carrot += 1
        elif choice == 2:
            world.add_object(w, y,"apple", 1)
            nb_apple += 1

    for x in range(w - 1, 1, -1):
        choice = random.randint(1,3)
        if choice == 1:
            world.add_object(x, h, "carrot", 1)
            nb_carrot += 1
        elif choice == 2:
            world.add_object(x, h,"apple", 1)
            nb_apple += 1
    
    for y in range(h - 1, 2, -1):
        choice = random.randint(1,3)
        if choice == 1:
            world.add_object(1, y, "carrot", 1)
            nb_carrot += 1
        elif choice == 2:
            world.add_object(1, y, "apple", 1)
            nb_apple += 1
    
    world.add_repoter_goal("I counted {} carrots and {} apples".format(nb_carrot, nb_apple))


def generate_maze():
    world =  WorldModel('./worlds/four.json', init)
    return Maze(world)