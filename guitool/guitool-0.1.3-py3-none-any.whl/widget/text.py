#!/usr/bin/python3
# -*- coding: utf8 -*-


class Text:
    def __init__(self, x1: int, y1: int, context, **kwargs):
        """
        This widget allows you to create text
        :param x1: int
        :param y1: int
        :param context: => context tkinter (here canvas)
        :param kwargs: Can be composed of (all optional) :{
        "fill": color of text (str ex:"red" or color hex ex:"#FF0000")
        "text": create text (str)
        "anchor": place the text (str)
        }
        """
        # Initializes mandatory attributes
        self.x1 = x1
        self.y1 = y1
        self.context = context

        # Init text
        self.text = kwargs.get("text", None)
        self.anchor = kwargs.get("anchor", "center")
        self.fill = kwargs.get("fill", "black")

        # Init other attribut
        self.item_tk = []
        self.item_name = "text"

    def draw(self):

        if len(self.item_tk) > 0:
            for item in self.item_tk:
                self.context.delete(item)

        item = self.context.create_text(
            self.x1,
            self.y1,
            text=self.text,
            anchor=self.anchor,
            fill=self.fill,
        )
        self.item_tk.append(item)

    def update(self, **kwargs):
        self.text = kwargs.get("text", self.text)
        self.fill = kwargs.get("fill", self.fill)

        self.draw()
