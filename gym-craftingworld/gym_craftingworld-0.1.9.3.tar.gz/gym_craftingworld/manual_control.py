#!/usr/bin/env python3

import time
import argparse
import numpy as np
import gym
import gym_craftingworld
from gym.envs.registration import register
from gym_craftingworld.envs.craftingworld_env_rgb import CraftingWorldEnvRGB

register(id='craftingworldNotFixedBinaryFiveTasks-v0',
         entry_point='gym_craftingworld.envs:CraftingWorldEnvRGB',
         kwargs={'size': (8, 8), 'store_gif': False, 'render_flipping': True, 'binary_rewards': True,
                 'selected_tasks': ['EatBread', 'MoveAxe', 'MoveHammer', 'GoToHouse', 'MoveSticks'], 'stacking': False,
                 'max_steps': 100}
         )

import sys
import numpy as np

# Only ask users to install matplotlib if they actually need it

import matplotlib.pyplot as plt
class Window:
    """
    Window to draw a gridworld instance using Matplotlib
    """

    def __init__(self, title):
        self.fig = None

        self.imshow_obj = None

        # Create the figure and axes
        self.fig, self.ax = plt.subplots()

        # Show the env name in the window title
        self.fig.canvas.set_window_title(title)

        # Turn off x/y axis numbering/ticks
        self.ax.xaxis.set_ticks_position('none')
        self.ax.yaxis.set_ticks_position('none')
        _ = self.ax.set_xticklabels([])
        _ = self.ax.set_yticklabels([])

        # Flag indicating the window was closed
        self.closed = False

        # def close_handler(evt):
        #     print("k")
        #     self.closed = True
        #
        # self.fig.canvas.mpl_connect('close_event', close_handler)

    def show_img(self, img):
        """
        Show an image or update the image being shown
        """

        # Show the first image of the environment
        if self.imshow_obj is None:
            self.imshow_obj = self.ax.imshow(img, interpolation='bilinear')

        self.imshow_obj.set_data(img)
        self.fig.canvas.draw()

        # Let matplotlib process UI events
        # This is needed for interactive mode to work properly
        plt.pause(0.001)

    def set_caption(self, text):
        """
        Set/update the caption text below the image
        """

        plt.xlabel(text)

    def reg_key_handler(self, key_handler):
        """
        Register a keyboard event handler
        """

        # Keyboard handler
        self.fig.canvas.mpl_connect('key_press_event', key_handler)

    def show(self, block=True):
        """
        Show the window, and start an event loop
        """
        print("Asd")
        # If not blocking, trigger interactive mode
        # if not block:
        #     plt.ion()

        # Show the plot
        # In non-interative mode, this enters the matplotlib event loop
        # In interactive mode, this call does not block
        plt.show(block=True)
        # plt.ion()

    def close(self):
        """
        Close the window
        """
        print("q")
        plt.close()
        self.closed = True


def ndtotext(A, w=None, h=None):
    if A.ndim == 1:
        if w == None:
            return str(A)
        else:

            entry = "\033[1m" + str(A[0]) if sum(A) != 0 else "\033[37m" + str(A[0])
            if np.array_equal(A, [2,5,0]) or np.array_equal(A, [1,0,0]):
                entry = "\033[37m" + str(A[0])
            s = '[' + ' ' * (max(w[-1], len(str(A[0]))) - len(str(A[0]))) + entry
            for i, AA in enumerate(A[1:]):
                # print(w[i], len(str(AA)) - len(str(AA)) + 1,str(AA))
                # print('  ',A[i-1], len(str(A[i-1])) - len(str(A[i-1])) + 1, str(A[i-1]))
                s += ' ' * (3-len(str(A[i]))) + str(AA)
            s += '\033[0m] '
    elif A.ndim == 2:
        w1 = [max([len(str(s)) for s in A[:, i]]) for i in range(A.shape[1])]
        print(w1)
        w0 = sum(w1) + len(w1) + 1
        print(w0)
        s = ''
        s = u'\u250c' + u'\u2500' * w0 + u'\u2510' + '\n'
        for AA in A:
            s += ' ' + ndtotext(AA, w=w1) + '\n'
        # s += u'\u2514' + u'\u2500' * w0 + u'\u2518'
    elif A.ndim == 3:
        h = A.shape[1]
        s1 = u'\u250c' + '\n' + (u'\u2502' + '\n') * h + u'\u2514' + '\n'
        s2 = u'\u2510' + '\n' + (u'\u2502' + '\n') * h + u'\u2518' + '\n'
        strings = [ndtotext(a) + '\n' for a in A]
        # strings.append(s2)
        # strings.insert(0, s1)
        s = '\n'.join(''.join(pair) for pair in zip(*map(str.splitlines, strings)))
    return s


def redraw(img):

    img = env.render(tile_size=args.tile_size)

    window.show_img(img)


def reset():
    if args.seed != -1:
        env.seed(args.seed)

    obs = env.reset()

    if hasattr(env, 'mission'):
        print('Mission: %s' % env.mission)
        window.set_caption(env.mission)

    redraw(obs)
    try:
        print(ndtotext(obs['image']))
    except:
        print("a")


def step(action):
    obs, reward, done, info = env.step(action)
    print('step=%s, reward=%.2f' % (env.step_count, reward))

    try:
        print(ndtotext(obs['image']))
    except:
        print("a")
    # print(obs['direction'],obs['mission'])

    if done:
        print('done!')
        reset()
    else:
        redraw(obs)

def key_handler(event):
    print('pressed', event.key)

    if event.key == 'escape':
        window.close()
        return

    if event.key == 'backspace':
        env.reset()
        return

    if event.key == 'a':
        env.step(3)
        return
    if event.key == 'd':
        env.step(1)
        return
    if event.key == 'w':
        env.step(0)
        return
    if event.key == 's':
        env.step(2)
        return

    # Spacebar
    if event.key == ' ':
        env.step(4)
        return
    if event.key == 'e':
        env.step(5)
        return


parser = argparse.ArgumentParser()
parser.add_argument(
    "--env",
    help="gym environment to load",
    default='craftingworldNotFixedBinaryFiveTasks-v0'
)
parser.add_argument(
    "--seed",
    type=int,
    help="random seed to generate the environment with",
    default=-1
)
parser.add_argument(
    "--tile_size",
    type=int,
    help="size at which to render tiles",
    default=32
)


args = parser.parse_args()

env = gym.make(args.env)




window = Window('gym_minigrid - ' + args.env)
window.reg_key_handler(key_handler)

reset()

# Blocking event loop
window.show(block=True)
print('b')

