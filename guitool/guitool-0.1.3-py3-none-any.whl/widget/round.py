#!/usr/bin/python3
# -*- coding: utf8 -*-


class Round:
    def __init__(self, x1: int, y1: int, x2: int, y2: int, context, **kwargs):
        """
        This widget allows you to create circles or ovals
        :param x1: int
        :param y1: int
        :param x2: int
        :param y2: int
        :param context: => context tkinter (here canvas)
        :param kwargs: Can be composed of (all optional) :{
        "square_fill": color of square (str ex:"red" or color hex ex:"#FF0000")
        "fill": color of round (str ex:"red" or color hex ex:"#FF0000")
        "width": frame width (int)
        "fill_mouse": color of the circle if the mouse hovers it
        (str ex:"red" or color hex ex:"#FF0000")
        "square_fill_mouse": color of the square if the mouse hovers it
        (str ex:"red" or color hex ex:"#FF0000")
        "command": couple of command action and effect (action, effet) or
        (action, effet, action, effet, etc..) ex:
        ("<Button-1>", "self.quit_gui")
        }
        """

        # Initializes mandatory attributes
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.context = context

        # Init optional attributes
        self.square_fill = kwargs.get("square_fill", None)
        self.fill = kwargs.get("fill", "grey")
        self.width = kwargs.get("width", 1)
        self.fill_mouse = kwargs.get("fill_mouse", self.fill)
        self.square_fill_mouse = kwargs.get("square_fill_mouse", self.square_fill)

        # Init command
        command = kwargs.get("command", None)
        self.command = {}
        if command is not None:
            index = 0
            count = int(len(command) / 2)
            if count == 1:
                c = command[index + 1]
                self.command[command[index]] = c
            else:
                for i in range(count):
                    a = command[index + 1]
                    self.command[command[index]] = a
                    index += 2

        # Init other attribut
        self.active_focus = False
        self.item_tk = []
        self.x = 0
        self.y = 0
        self.item_name = "round"

    def draw(self):
        if len(self.item_tk) > 0:
            for item in self.item_tk:
                self.context.delete(item)
            self.item_tk = []

        if self.square_fill is not None:
            item = self.context.create_rectangle(
                self.x1,
                self.y1,
                self.x2,
                self.y2,
                fill=self.square_fill,
                width=self.width,
            )
            self.item_tk.append(item)

        item = self.context.create_oval(
            self.x1, self.y1, self.x2, self.y2, fill=self.fill, width=self.width
        )
        self.item_tk.append(item)

    def draw_focus(self):
        if self.square_fill is not None or self.fill_mouse is not None:
            if len(self.item_tk) > 0:
                for item in self.item_tk:
                    self.context.delete(item)
                self.item_tk = []

        if self.square_fill is not None:
            item = self.context.create_rectangle(
                self.x1,
                self.y1,
                self.x2,
                self.y2,
                fill=self.square_fill_mouse,
                width=self.width,
            )
            self.item_tk.append(item)

        if self.fill_mouse is not None:
            item = self.context.create_oval(
                self.x1,
                self.y1,
                self.x2,
                self.y2,
                fill=self.fill_mouse,
                width=self.width,
            )
            self.item_tk.append(item)

    def update(self, **kwargs):
        self.fill = kwargs.get("fill", self.fill)
        self.fill_mouse = kwargs.get("fill_mouse", self.fill)

        if self.x1 < self.x < self.x2 and self.y1 < self.y < self.y2:
            self.draw_focus()
        else:
            self.draw()

    def motion(self, x, y):
        self.x = x
        self.y = y

        if self.x1 < x < self.x2 and self.y1 < y < self.y2:
            if not self.active_focus:
                self.draw_focus()
                self.active_focus = True

        else:
            if self.active_focus:
                self.draw()
                self.active_focus = False

    def commande(self, x, y, action):

        if action in self.command:
            if self.x1 < x < self.x2 and self.y1 < y < self.y2:
                self.command[action]()
