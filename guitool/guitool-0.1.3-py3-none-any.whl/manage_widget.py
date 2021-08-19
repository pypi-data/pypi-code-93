#!/usr/bin/python3
# -*- coding: utf8 -*-

from tk_gui_tools.widget.rectangle import Rectangle
from tk_gui_tools.widget.round import Round
from tk_gui_tools.widget.text import Text
from tk_gui_tools.widget.menu import Menu
from tk_gui_tools.widget.button import Button


class ManageWidget:
    """
    ManageWidget manages widgets
    """

    def __init__(self, context):
        """
        :param context: Canvas instance
        """
        self.context = context

        # Init the list item for action
        self.list_item = []

        # Init attribute mouse
        self.x = 0
        self.y = 0
        self.action = None

    def create_rectangle(self, x1: int, y1: int, x2: int, y2: int, **kwargs):
        """
        Create rectangle
        :param x1: int
        :param y1: int
        :param x2: int
        :param y2: int
        :param kwargs: Can be composed of (all optional) :{
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
        }
        :return: item (instance rectangle)
        """

        item = Rectangle(x1, y1, x2, y2, self.context, **kwargs)
        item.draw()
        self.list_item += [item]
        return item

    def create_round(self, x1: int, y1: int, x2: int, y2: int, **kwargs):
        """
        Create round
        :param x1: int
        :param y1: int
        :param x2: int
        :param y2: int
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
        :return: item (instance round)
        """

        item = Round(x1, y1, x2, y2, self.context, **kwargs)
        item.draw()
        self.list_item += [item]
        return item

    def create_text(self, x1: int, y1: int, **kwargs):
        """
        This widget allows you to create text
        :param x1: int
        :param y1: int
        :param kwargs: Can be composed of (all optional) :{
        "fill": color of text (str ex:"red" or color hex ex:"#FF0000")
        "text": create text (str)
        "anchor": place the text (str)
        }
        :return: item (instance text)
        """

        item = Text(x1, y1, self.context, **kwargs)
        item.draw()
        return item

    def create_menu(self, x1: int, y1: int, x2: int, y2: int, **kwargs):
        """
        This widget allows you to create menu
        :param x1: int
        :param y1: int
        :param x2: int
        :param y2: int
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
        :return: item (instance menu)
        """

        item = Menu(x1, y1, x2, y2, self.context, **kwargs)
        item.draw()
        self.list_item += [item]
        return item

    def create_button(self, x1: int, y1: int, **kwargs):
        """
        This widget allows you to create button
        :param x1: int
        :param y1: int
        :param kwargs: {
        "active": Set default state of button (Bool)
        "fill_round": color of round (str ex:"red" or color hex ex:"#FF0000")
        "fill_body": color of body (str ex:"red" or color hex ex:"#FF0000")
        "scale": set the scale (float)
        :return: item (instance button)
        """

        item = Button(x1, y1, self.context, **kwargs)
        item.draw()
        self.list_item += [item]
        return item

    def motion(self, x, y):
        self.x = x
        self.y = y

        for item in self.list_item:
            item.motion(x, y)

    def command(self, x, y, action):
        self.action = action

        for item in self.list_item:
            item.commande(x, y, action)
