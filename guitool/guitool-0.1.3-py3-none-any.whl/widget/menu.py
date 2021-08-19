#!/usr/bin/python3
# -*- coding: utf8 -*-

from tk_gui_tools.widget.rectangle import Rectangle


class Menu(Rectangle):
    def __init__(self, x1, y1, x2, y2, context, **kwargs):
        """
        This widget allows you to create menu
        :param x1: int
        :param y1: int
        :param x2: int
        :param y2: int
        :param context: => context tkinter (here canvas)
        :param kwargs: {
        "fill": color of round (str ex:"red" or color hex ex:"#FF0000")
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
        """
        Rectangle.__init__(
            self,
            x1,
            y1,
            x2,
            y2,
            context,
            command=("<Button-1>", self.label_draw),
            **kwargs
        )
        # Init other attribut
        self.label = []
        self.cascade = {}
        self.label_active = False
        self.label_surface = [0, 0]
        self.item_name = "menu"

    def add_label(self, text, **kwargs):
        """
        Add label link a menu method
        :param text: str
        :param kwargs:
        :return: indice label (int)
        """
        # TODO remplacer lg et ht par une fonction
        #  qui calcule la dimension en pixel du texte
        lg = 100
        ht = 20
        context = self.context

        if len(self.label) == 0:
            x1 = self.x1
            y1 = self.y2 + 1
            x2 = x1 + lg
            y2 = y1 + ht
            self.label_surface[0] = x2
            self.label_surface[1] += y2
        else:
            x1 = self.x1
            y1 = self.label[-1].y2
            x2 = x1 + lg
            y2 = y1 + ht
            self.label_surface[0] = x2
            self.label_surface[1] += y2

        item = Rectangle(
            x1,
            y1,
            x2,
            y2,
            context,
            fill="#DCDCDC",
            fill_mouse="blue",
            text=text,
            text_fill_mouse="white",
            width=0,
            **kwargs
        )
        item.menu_type = "label"
        self.label.append(item)
        return len(self.label) - 1

    def add_cascade(self, text, item, **kwargs):
        """
        Add cascade link a label method
        :param text: str
        :param item: indice label (int)
        :param kwargs:
        """
        # TODO remplacer lg et ht par une fonction
        #  qui calcule la dimension en pixel du texte
        lg = 100
        ht = 20
        target = self.label[item]
        context = self.context
        if target in self.cascade:
            x1 = self.cascade[target][-1].x1
            y1 = self.cascade[target][-1].y2
            x2 = x1 + lg
            y2 = y1 + ht

        else:
            self.cascade[target] = []
            x1 = target.x2
            y1 = target.y1
            x2 = x1 + lg
            y2 = y1 + ht

        item = Rectangle(
            x1,
            y1,
            x2,
            y2,
            context,
            fill="#DCDCDC",
            fill_mouse="blue",
            text=text,
            text_fill_mouse="white",
            width=0,
            **kwargs
        )
        item.menu_type = "cascade"
        item.target = target
        self.cascade[target].append(item)
        target.command["<Button-1>"] = self.cascade_draw
        target.menu_type = "target cascade"
        target.cascade_active = False

    def cascade_draw(self):
        """
        Active cascade, window lateral
        """

        for item in self.label:
            if "target cascade" in item.menu_type:
                if item.active_focus:
                    if item in self.cascade:
                        if not item.cascade_active:
                            for item_cascade in self.cascade[item]:
                                item_cascade.draw()
                            item.cascade_active = True
                        else:
                            for item_cascade in self.cascade[item]:
                                if len(item_cascade.item_tk) > 0:
                                    for item_tk in item_cascade.item_tk:
                                        self.context.delete(item_tk)
                            item.cascade_active = False
                elif item.cascade_active:
                    for item_cascade in self.cascade[item]:
                        if len(item_cascade.item_tk) > 0:
                            for item_tk in item_cascade.item_tk:
                                self.context.delete(item_tk)
                    item.cascade_active = False

    def label_draw(self):
        """
        Active label window bottom
        """

        if not self.label_active:
            for item in self.label:
                item.draw()
            self.label_active = True
        else:
            for item in self.label:
                if "target cascade" in item.menu_type:
                    if item.cascade_active:
                        for item_cascade in self.cascade[item]:
                            if len(item_cascade.item_tk) > 0:
                                for item_tk in item_cascade.item_tk:
                                    self.context.delete(item_tk)
                        item.cascade_active = False
                if len(item.item_tk) > 0:
                    for item in item.item_tk:
                        self.context.delete(item)
            self.label_active = False

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

        if self.label_active:
            for item in self.label:
                item.motion(x, y)
                if "target cascade" in item.menu_type:
                    if item.cascade_active:
                        for item_cascade in self.cascade[item]:
                            item_cascade.motion(x, y)

    def commande(self, x, y, action):

        if self.label_active:
            for item in self.label:
                if "target cascade" in item.menu_type:
                    if item.cascade_active:
                        for item_cascade in self.cascade[item]:
                            item_cascade.commande(x, y, action)
                item.commande(x, y, action)

        if action in self.command:
            if self.x1 < x < self.x2 and self.y1 < y < self.y2:
                self.command[action]()
            else:
                if self.label_active:
                    if not (
                        self.x1 < x < self.label_surface[0]
                        and self.y1 < y < self.label_surface[1]
                    ):
                        self.command[action]()
