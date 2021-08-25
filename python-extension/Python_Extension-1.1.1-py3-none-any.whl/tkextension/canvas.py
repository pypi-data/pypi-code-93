import sys
if sys.version_info[0] != 3 or sys.version_info[1] < 6:
    raise SystemExit('This module needs Python 3.6 or more later')

from tkinter import *
from tkinter.colorchooser import *

raise SystemExit('This module is not supported')

class Create():
    def __init__(self, tkinter_attribute, canvas_attribute):
        self.tk = tkinter_attribute
        self.window = canvas_attribute
    def create(self, shape=['dot', 'line', 'triangle', 'rectangle', 'square', 'oval', 'circle'], args=(10, 10, 5, 5, 'SE', 'red')):# dotx, doty, distance, width, angle, fill
        x = args[2]
        y = args[3]
        try:
            color = args[2]
        except IndexError:
            color = 'black'
        match shape:
            case 'dot':
                get = self.window.create_oval(dotx-1, doty-1, dotx+1, doty+1, fill=color)
                return get
            case 'line':
                match args[4]:
                    case 'SE':
                        get = self.window.create_line(dotx, doty, dotx+x, doty-x, fill=color, width=y)
                        return get
                    case 'NE':
                        get = self.window.create_line(dotx, doty, dotx+x, doty+x, fill=color, width=y)
                        return get
                    case 'SW':
                        get = self.window.create_line(dotx, doty, dotx-x, doty-x, fill=color, width=y)
                        return get
                    case 'NW':
                        get = self.window.create_line(dotx, doty, dotx-x, doty+x, fill=color, width=y)
                        return get
                    case 'E':
                        get = self.window.create_line(dotx, doty, dotx+x, doty, fill=color, width=y)
                        return get
                    case 'W':
                        get = self.window.create_line(dotx, doty, dotx-x, doty, fill=color, width=y)
                        return get
                    case 'N':
                        get = self.window.create_line(dotx, doty, dotx, doty+x, fill=color, width=y)
                        return get
                    case 'S':
                        get = self.window.create_line(dotx, doty, dotx, doty-x, fill=color, width=y)
                        return get
                    case _:
                        raise ValueError('\'angle\' must be SE, NE, SW, NW, E, W, N, S')
            case 'triangle':
                pass

