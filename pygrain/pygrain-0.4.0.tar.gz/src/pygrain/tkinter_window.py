import tkinter as tk


class TkinterWindow(tk.Tk):
    def __init__(self, parent_app, width='', height='', x=None, y=None):
        super().__init__()
        geometry = str(width) + 'x' + str(height)
        if x and y:
            geometry += str(x) + '+' + str(y)
        self.geometry(geometry)
        parent_app.add_tkinter_window(self)