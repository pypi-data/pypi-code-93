#!/usr/bin/python3
# -*- coding: utf8 -*-


class Button:
    def __init__(self, x: int, y: int, context, **kwargs):
        """
        This widget allows you to create button
        :param x: int
        :param y: int
        :param context: => context tkinter (here canvas)
        :param kwargs: {
        "active": Set default state of button (Bool)
        "fill_round": color of round (str ex:"red" or color hex ex:"#FF0000")
        "fill_body": color of body (str ex:"red" or color hex ex:"#FF0000")
        "scale": set the scale (float)
        """

        self.x = x
        self.y = y
        self.context = context
        self.active = kwargs.get("active", False)
        self.fill_round = kwargs.get("fill_round", "red")
        self.fill_body = kwargs.get("fill_body", "blue")
        self.scale = kwargs.get("scale", 1)

        v1 = 30 * self.scale
        v2 = 10 * self.scale

        # Init command
        self.command = {"<Button-1>": self.active_button}

        self.x1 = self.x - v1
        self.x2 = self.x + v1
        self.y1 = self.y - v2
        self.y2 = self.y + v2

        self.round = {
            "x1": self.x - v1,
            "y1": self.y - v2,
            "x2": self.x - v2,
            "y2": self.y + v2,
        }
        self.rectangle = {
            "x1": self.x - (self.round["x2"] - self.round["x1"]),
            "y1": self.y - v2,
            "x2": self.x + (self.round["x2"] - self.round["x1"]) + 1,
            "y2": self.y + v2,
        }
        self.arc = {
            "x1": self.x + v1,
            "y1": self.y - v2,
            "x2": self.x + v2,
            "y2": self.y + v2,
            "start": -90,
            "extent": 180,
        }

        # Init other attribut
        self.item_tk = []

    def active_button(self):
        if not self.active:
            v1 = -30
            v2 = -10
            self.round = {
                "x1": self.x - v1,
                "y1": self.y - v2,
                "x2": self.x - v2,
                "y2": self.y + v2,
            }
            self.rectangle = {
                "x1": self.x - (self.round["x2"] - self.round["x1"]),
                "y1": self.y - v2,
                "x2": self.x + (self.round["x2"] - self.round["x1"]),
                "y2": self.y + v2 + 1,
            }
            self.arc = {
                "x1": self.x + v1,
                "y1": self.y - v2,
                "x2": self.x + v2,
                "y2": self.y + v2,
                "start": 90,
                "extent": 180,
            }
            self.active = True
            self.draw()
        else:
            v1 = 30
            v2 = 10
            self.round = {
                "x1": self.x - v1,
                "y1": self.y - v2,
                "x2": self.x - v2,
                "y2": self.y + v2,
            }
            self.rectangle = {
                "x1": self.x - (self.round["x2"] - self.round["x1"]),
                "y1": self.y - v2,
                "x2": self.x + (self.round["x2"] - self.round["x1"]) + 1,
                "y2": self.y + v2 + 1,
            }
            self.arc = {
                "x1": self.x + v1,
                "y1": self.y - v2,
                "x2": self.x + v2,
                "y2": self.y + v2,
                "start": -90,
                "extent": 180,
            }
            self.active = False
            self.draw()

    def draw(self):
        if len(self.item_tk) > 0:
            for item in self.item_tk:
                self.context.delete(item)
            self.item_tk = []

        item = self.context.create_arc(
            self.arc["x1"],
            self.arc["y1"],
            self.arc["x2"],
            self.arc["y2"],
            start=self.arc["start"],
            extent=self.arc["extent"],
            fill=self.fill_body,
            width=0,
        )
        self.item_tk.append(item)

        item = self.context.create_rectangle(
            self.rectangle["x1"],
            self.rectangle["y1"],
            self.rectangle["x2"],
            self.rectangle["y2"],
            width=0,
            fill=self.fill_body,
        )
        self.item_tk.append(item)
        item = self.context.create_oval(
            self.round["x1"],
            self.round["y1"],
            self.round["x2"],
            self.round["y2"],
            fill=self.fill_round,
        )
        self.item_tk.append(item)

    def commande(self, x, y, action):

        if action in self.command:
            if self.x1 < x < self.x2 and self.y1 < y < self.y2:
                self.command[action]()

    def motion(self, x, y):
        """
        not implemented
        :param x:
        :param y:
        :return:
        """

        if self.x1 < x < self.x2 and self.y1 < y < self.y2:
            pass
