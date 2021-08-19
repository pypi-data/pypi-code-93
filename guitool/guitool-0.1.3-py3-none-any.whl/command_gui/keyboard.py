#!/usr/bin/python3
# -*- coding: utf8 -*-


class Keyboard:
    """
    Manage keyboard events
    """

    def __init__(self):

        # key press alt + enter
        self.window.bind("<Alt-Return>", self.fullscreen)
