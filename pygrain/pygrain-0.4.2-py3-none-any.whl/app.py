import pygame
import sys
import os
import ctypes
import threading
import tkinter as tk
import platform


# For graphics quality
ctypes.windll.shcore.SetProcessDpiAwareness(1)

# Position of pygame window from top left of screen
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (5, 60)

WHITE = 255, 255, 255


class App:
    """
    Class to create and run new application.
    """

    def __init__(self, width=1000, height=800, frame=None):
        self.width, self.height = width, height
        self.screen = None
        self.frame = frame
        self.frames = []
        self.UPDATE = True
        self.x, self.y = 0, 0
        self.windows = []
        self.running = True

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))

    def mainloop(self):
        """
        Initialise the display.
        Check for events and update display when required.
        """
        while self.running:
            self.check_events()
            if not self.running:
                break
            if self.UPDATE:
                self.UPDATE = False
                self.screen.fill(WHITE)

                if self.frame:
                    self.frame.draw(self.screen)

                pygame.display.update()
                for window in self.windows:
                    try:
                        window.update()
                    except tk.TclError:
                        pass

    def update(self):
        """
        Set UPDATE flag.
        :return: self
        """
        self.UPDATE = True
        return self

    def add_component(self, frame):
        """
        Add frame to list of frames
        :param frame: a new Frame object
        :return: None
        """
        self.frames.append(frame)

    def check_events(self):
        """
        Check for keyboard and mouse events and pass them to the current frame.
        :return: None
        """
        events = pygame.event.get()
        current_event = set()
        current_event.add('always')
        for event in events:
            if event.type == pygame.QUIT:
                self.close()

            if event.type == pygame.MOUSEBUTTONDOWN:
                current_event.add('click')
                if event.button == 1:
                    current_event.add("left click")
                elif event.button == 2:
                    current_event.add("middle click")
                elif event.button == 3:
                    current_event.add("right click")
                elif event.button == 4:
                    current_event.add("scroll up")
                elif event.button == 5:
                    current_event.add("scroll down")

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    current_event.add("left up")
                elif event.button == 2:
                    current_event.add("middle up")
                elif event.button == 3:
                    current_event.add("right up")

            elif event.type == pygame.MOUSEMOTION:
                current_event.add("mousemotion")

        if self.frame:
            self.frame.event(current_event)

    def switch_frame(self, frame):
        """
        Set the current frame
        :param frame:
        :return: self
        """
        self.frame = frame
        return self

    def run(self, func):
        """
        Create new thread from for given function and start thread.
        :param func:
        :return: self
        """
        window_thread = threading.Thread(target=func, args=tuple())
        window_thread.start()

        return self

    def add_tkinter_window(self, window):
        self.windows.append(window)

    def set_title(self, title):
        """
        Set title for pygame window.
        :param title: name of pygame window
        :return:
        """
        pygame.display.set_caption(title)
        return self

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_abs_x(self):
        return self.x

    def get_abs_y(self):
        return self.y

    def is_running(self):
        return self.running

    def close(self):
        self.running = False
        pygame.quit()

