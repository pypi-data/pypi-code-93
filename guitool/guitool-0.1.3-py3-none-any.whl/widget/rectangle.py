#!/usr/bin/python3
# -*- coding: utf8 -*-


class Rectangle:
    def __init__(self, x1: int, y1: int, x2: int, y2: int, context, **kwargs):
        """
        This widget allows you to create rectangle
        :param x1: int
        :param y1: int
        :param x2: int
        :param y2: int
        :param context: => context tkinter (here canvas)
        :param kwargs: Can be composed of (all optional) :{
        "fill": color (str ex:"red" or color hex ex:"#FF0000")
        "width": frame width (int)
        "text": create text (str)
        "anchor": place the text (str)
        "text_fill": color the text (str ex:"red" or color hex ex:"#FF0000")
        "text_fill_mouse": color the text if the mouse hovers it
        (str ex:"red" or color hex ex:"#FF0000")
        "fill_mouse": color of the circle if the mouse hovers it
        (str ex:"red" or color hex ex:"#FF0000")
        "command": couple of command action and effect (action, effet) or
        (action, effet, action, effet, etc..) ex:
        ("<Button-1>", "self.quit_gui")
        "relief": active the relief (bool)
        }
        """

        # Initializes mandatory attributes
        self.context = context
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

        # Init optional attributes
        self.fill = kwargs.get("fill", "grey")
        self.fill_mouse = kwargs.get("fill_mouse", self.fill)
        self.text = kwargs.get("text", None)
        self.width = kwargs.get("width", 1)

        # Init text
        if self.text is not None:
            self.text_fill = kwargs.get("text_fill", "black")
            self.text_fill_mouse = kwargs.get("text_fill_mouse", "black")
            self.anchor = kwargs.get("anchor", "center")
            if self.anchor == "center":
                self.text_x = (self.x2 - self.x1) / 2 + self.x1
                self.text_y = (self.y2 - self.y1) / 2 + self.y1

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

        # Init relief
        self.relief = kwargs.get("relief", False)
        if self.relief:
            self.ligne_1 = [self.x1, self.y2, self.x2, self.y2]
            self.ligne_2 = [self.x2, self.y1, self.x2, self.y2]

        # Init other attribut
        self.active_focus = False
        self.item_tk = []
        self.x = 0
        self.y = 0
        self.item_name = "rectangle"

    def draw(self):
        if len(self.item_tk) > 0:
            for item in self.item_tk:
                self.context.delete(item)
            self.item_tk = []

        item = self.context.create_rectangle(
            self.x1, self.y1, self.x2, self.y2, fill=self.fill, width=self.width
        )
        self.item_tk.append(item)
        if self.text is not None:
            item = self.context.create_text(
                self.text_x,
                self.text_y,
                text=self.text,
                fill=self.text_fill,
                anchor=self.anchor,
            )
            self.item_tk.append(item)
        if self.relief:
            item = self.context.create_line(
                self.ligne_1[0],
                self.ligne_1[1],
                self.ligne_1[2],
                self.ligne_1[3],
                width=1,
            )
            self.item_tk.append(item)
            item = self.context.create_line(
                self.ligne_2[0],
                self.ligne_2[1],
                self.ligne_2[2],
                self.ligne_2[3],
                width=1,
            )
            self.item_tk.append(item)

    def draw_focus(self):
        if len(self.item_tk) > 0:
            for item in self.item_tk:
                self.context.delete(item)
            self.item_tk = []

        item = self.context.create_rectangle(
            self.x1, self.y1, self.x2, self.y2, fill=self.fill_mouse, width=self.width
        )
        self.item_tk.append(item)
        if self.text is not None:
            item = self.context.create_text(
                self.text_x,
                self.text_y,
                text=self.text,
                fill=self.text_fill_mouse,
                anchor=self.anchor,
            )
            self.item_tk.append(item)
        if self.relief:
            item = self.context.create_line(
                self.ligne_1[0],
                self.ligne_1[1],
                self.ligne_1[2],
                self.ligne_1[3],
                width=2,
            )
            self.item_tk.append(item)
            item = self.context.create_line(
                self.ligne_2[0],
                self.ligne_2[1],
                self.ligne_2[2],
                self.ligne_2[3],
                width=2,
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
