#!/usr/bin/python3
# -*- coding: utf8 -*-

import tkinter as tk

# Instance
import tk_gui_tools.manage_widget as manage_widget

# Heritage
from tk_gui_tools.command_gui.mouse import Mouse
from tk_gui_tools.command_gui.keyboard import Keyboard
from tk_gui_tools.command_gui.command import CommandGUI
from tk_gui_tools.tool.scroolbar import ScrollBar


class Base(Mouse, Keyboard, CommandGUI, ScrollBar):
    """
    Base is a pre-filled template to inherit and use command functionality
    """

    def __init__(self, window):

        # width screen
        self.width = window.winfo_screenwidth()
        # height screen
        self.height = window.winfo_screenheight()

        # Create the Canvas
        self.canvas = tk.Canvas(
            window,
            height=self.height,
            width=self.width,
            bg="grey",
            scrollregion=(0, 0, self.width, self.height),
        )

        # Instance
        self.window = window
        self.manage = manage_widget.ManageWidget(self.canvas)

        # Init ScrollBar Héritage
        ScrollBar.__init__(self)

        # Init Keyboard and Mouse Héritage
        Keyboard.__init__(self)
        Mouse.__init__(self)

        self.canvas.pack(fill=tk.BOTH, side=tk.LEFT, expand=tk.TRUE)

    def update(self):
        """
        Update the template
        """

        self.canvas.update_idletasks()
