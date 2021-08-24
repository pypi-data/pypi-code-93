from .robot import Robot
from .maze import Maze
from .models.world_model import WorldModel 
import random
from IPython.core.display import HTML

def get_robo_builder(**kwargs):
    levels = kwargs.get("levels", {})
    robo_fn = kwargs.get("robo_fn", {})

    def blank(world):
        pass

    def load_world(level):
        return WorldModel(f"./worlds/{level}.json", levels.get(level, blank))

    def robo_class():
        return robot

    def print_description(level):
        world = load_world(level)
        return HTML(world.description)

    def bot_init(maze, level):
        bot = maze.bot()
        fn = robo_fn.get(level, blank)
        fn(bot)
        

    def generate_maze(level):
        world = load_world(level)
        maze = Maze(world)
        bot_init(maze, level)
        return maze

    def get_bot(level):
        maze = generate_maze(level)
        bot = maze.bot()
        bot.set_trace('red')
        return bot
    
    return get_bot