#!/usr/bin/python3
# -*- coding: utf8 -*-

import tkinter as tk


class ScrollBar:
    """
    This class is a heritage of the Base template
    """

    def __init__(self):

        # Init scroolbar
        self.scroolbar_horzi = tk.Scrollbar(self.canvas)
        self.scroolbar_verti = tk.Scrollbar(self.canvas)

        self.canvas.config(
            xscrollcommand=self.scroolbar_horzi.set,
            yscrollcommand=self.scroolbar_verti.set,
        )

        self.scroolbar_horzi.config(orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scroolbar_verti.config(orient=tk.VERTICAL, command=self.canvas.yview)

        self.scroolbar_horzi.pack(fill=tk.X, side=tk.BOTTOM, expand=tk.FALSE)
        self.scroolbar_verti.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
