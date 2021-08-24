from ttgtcanvas2 import WorldModel, Maze
import random

def init(world): 
    world.add_flag_count_goal(2)
    # dictionary = { 'apple': 4, 'banana': 6, 'carrot': 9, 'daisy': 3, 'dandelion': 7, 'tulip': 8}
    # items = ["apple", "banana", "carrot", "daisy", "dandelion",   "tulip"]

    # for x in range(2, 3):
    #     count = random.randint(1,9)
    #     item = items[x - 2]
    #     world.add_object(x, 1, item, count)
        
    #     for y in range(count):
    #         world.add_drop_obj_goal(y+ 1, dictionary[item], item, 1)
    # world.add_home_goal(7, 1)
    

def generate_maze():
    world =  WorldModel('./worlds/test.json', init)
    return Maze(world)


    