from ttgtcanvas2 import WorldModel, Maze
import random

def choose_fruit():
    choice = random.randint(1,3)
    if choice == 1:
        return 'apple'
    elif choice == 2:
        return 'banana'
    else:
        return 'strawberry'


def init(world):
    cfruit = 0
    #Fruit to pick
    fruit = choose_fruit()
    world.add_object(3,1, fruit, 1)
    for x in range(3, 9):
        for y in range(3,9):
            f = choose_fruit()
            world.add_object(x,y, f, 1)
            if f == fruit:
                cfruit +=1

    world.add_repoter_goal("I counted {} {}".format(cfruit, fruit))
    





def generate_maze():
    world =  WorldModel('./worlds/five.json', init)
    return Maze(world)