#!/usr/bin/python3
# -*- coding: utf8 -*-


class Mouse:
    """
    Manage mouse events
    """

    def __init__(self):
        """
        Init mouse event
        """
        self.window.bind("<Double-Button-1>", self.double_click_button_1)
        self.window.bind("<Motion>", self.mouse_motion)
        self.window.bind("<Button-1>", self.click_button_1)

    def mouse_motion(self, event):
        """
        Capture mouse movement
        :param event: objet tkinter
        """

        self.adjust_mousse(event.x, event.y)
        self.manage.motion(self.x, self.y)

    def double_click_button_1(self, event):

        self.adjust_mousse(event.x, event.y)
        self.manage.command(self.x, self.y, "<Double-Button-1>")

    def click_button_1(self, event):

        self.adjust_mousse(event.x, event.y)
        self.manage.command(self.x, self.y, "<Button-1>")

    def adjust_mousse(self, x: int, y: int):
        """
        Adjusts the mouse pointer offset with the scrollbar offset
        :param x: int
        :param y: int
        """
        self.x_adjust = self.scroolbar_horzi.get()[0] * self.width
        self.x = x + self.x_adjust

        self.y_adjust = self.scroolbar_verti.get()[0] * self.height
        self.y = y + self.y_adjust
