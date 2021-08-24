from ttgtcanvas2 import get_robo_builder
import random

def init(world): 
#     dictionary = { 'apple': 4, 'banana': 6, 'carrot': 9, 'daisy': 3, 'dandelion': 7, 'tulip': 8}
#     items = ["apple", "banana", "carrot", "daisy", "dandelion",   "tulip"]

#     for x in range(2, 3):
#         count = random.randint(1,9)
#         item = items[x - 2]
#         world.add_object(x, 1, item, count)
        
#         for y in range(count):
#             world.add_drop_obj_goal(y+ 1, dictionary[item], item, 1)
    world.add_home_goal(7, 1)
    world.add_repoter_goal('Hi')
    world.add_repoter_goal('bye')
    world.add_flag_count_goal(2)
    
get_robo = get_robo_builder(levels={
    'test': init
},
robo_fn={
})